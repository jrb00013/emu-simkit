**The `0x17` write is the game crashing itself on purpose. The real bug is a main-thread stall of more than 30 s that happens before it.**

I reproduced this on 0.0.42-19984-961c86fb with BLUS31011 01.00 (PPU hash `PPU-fa8ffe9ae59bfa8575027c9a6ec5aab7fb0215ab`), in 2-player split-screen Zombies (TranZit). The crash came about 1.5 min after the map loaded. The fatal dump includes the disassembly of the `hang detect` thread's loop:

```
0041c3c8  lis   r3,0xcc ; lbz r3,-0x32f4(r3)   ; watchdog enabled?
0041c3d8  bl    0x41f270                      ; now (ms)
0041c3e4  lwz   r3,-0x32f8(r3)                ; last heartbeat [0xcbcd08]
0041c3f8  subfc r3,r3,r4
0041c3fc  cmpwi r3,0x7530                     ; > 30000 ms ?
0041c404  mr    r3,r31 ; bl 0x7c6398          ; prints "Hang detected."
0041c40c  li    r3,0x17
0041c410  li    r4,0x10e4
0041c414  stw   r4,0(r3)                      ; *(u32*)0x17 = 0x10e4  <- intentional crash
0041c428  li    r3,0x2710 ; bl 0x317a18       ; sleep 10 s, loop
```

The TTY shows `sys_tty_write(): "Hang detected."` right before the access violation. RPCS3 reports the absolute guest address (host fault pointer minus `vm::g_base_addr`), so nothing is wrong with memory mapping and no per-player struct is missing. The game's watchdog found that the main thread had not updated its heartbeat for 30 s and crashed deliberately. Other reports show the same pattern: #16426's original log (BLUS31141) crashes in `hang detect` at `0x00463064`, and the comment above noticed that RSX goes quiet about 40 s before the abort.

**What the stalled main thread is doing** (from the same dump):
- `main_thread` sits in a polling loop at `0x73d6ec..0x73d7b4`. Each pass does a 64-bit `ldarx/stdcx.` CAS, a `lwarx/stwcx.` exchange, then `bl 0x73d09c(*(0xccc740), 0, 1, r30)`, then `sys_timer_usleep(50)`. Its reservation is at `0x2e208a0`.
- Call stack: `0x73d7a8 <- 0x3aca08 <- 0x6dd2d4 <- 0x125128 <- 0x125538 <- 0x30084c <- 0x300b18 <- 0x41c18c <- 0x6450e0 <- 0x644e74`.
- Last RSX activity was at 0:53:29.65 and "Hang detected" at 0:54:08.67, 39 s later. That fits a >30 s threshold with a 10 s poll.
- The game is not frozen. Syscall counters per 10 s during the stall:

| Syscall | Calls per 10 s |
|---|---|
| `sys_timer_usleep` | +~110k (the main-thread spin) |
| `sys_semaphore_wait` | +~17k |
| `sys_semaphore_get_value` | +~10k |
| `sys_event_queue_receive` | +~8k |
| `sys_semaphore_post` | +~7.5k |
| `sys_spu_thread_read_ls` / `sys_spu_thread_write_spu_mb` | +~5.6k each |

  Over the same period `sys_rsx_context_attribute`, `sys_time_get_current_time` and the lwmutex calls stop entirely. Host CPU stayed around 55%.

So this looks like a livelock or lost wakeup: the main thread waits on a completion flag that some producer never sets. The producer is probably the game's job system (SPURS/SPU jobs, given the steady SPU mailbox and LS traffic). Split-screen roughly doubles the per-frame job load, which would explain why the bug only shows up there. This part is a hypothesis. I don't have the unpacked EBOOT to identify `0x73d09c` or what writes the flag.

**Why the current logs can't settle it:** the fatal dump only covers `main_thread` and the faulting thread. The faulting thread here is the watchdog, which is innocent. The thread that is actually stuck, or the SPU group that stopped signalling, never gets printed.

**Proposed RPCS3 change (diagnostic, not a fix):** on a fatal PPU access violation, also log a one-line summary of every other PPU thread (state, CIA/LR, current or last syscall, wait time, call stack) and every SPU thread (state, PC). It uses `idm::select(..., idm::unlocked)`, the same lock-free approach the existing dump uses. The diff touches `rpcs3/Emu/CPU/CPUThread.cpp` and `Utilities/Thread.cpp`, 74 added lines. I can open it as a PR if that's useful. It passes `g++-13 -fsyntax-only` on Linux. I have not built or run it fully.

**For anyone who can reproduce it:** NOP the intentional store so the emulator stays alive through the stall, then look at Debug > Kernel Explorer and the SPU thread group:

```yaml
PPU-fa8ffe9ae59bfa8575027c9a6ec5aab7fb0215ab:
  "Disable hang-detect deliberate crash (diagnostic only)":
    Games:
      "Call of Duty: Black Ops II":
        BLUS31011: [ 01.00 ]
    Author: "diagnostic"
    Notes: "Keeps the process alive when the watchdog fires; does NOT fix the stall."
    Patch Version: 1.0
    Patch:
      - [ be32, 0x0041c414, 0x60000000 ] # stw r4,0(r3) -> nop
```

If the game recovers after some time, the problem is a long starvation stall (SPU scheduling or timing). If it never recovers, it is a true deadlock or lost wakeup. Kernel Explorer then shows which semaphore, event queue or lwcond the other threads are blocked on. Settings worth A/B testing under split-screen: `Accurate SPU DMA`, `SPU Block Size` (Safe vs Mega), `Preferred SPU Threads`, and PPU/SPU `Accurate Reservations` / `Accurate Cache Line Stores`. RSX FIFO = Atomic has already been reported not to help.
