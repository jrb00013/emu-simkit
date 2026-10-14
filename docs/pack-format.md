# Pack format

A pack is a directory with `pack.yml`:

```yaml
name: my-pack
version: 0.1.0
description: optional
backend: generic
titles: [ TITLEID ]
patches: [ foo_patch.yml ]
overrides: [ overrides.yml ]
patch_config: patch_config.yml   # optional
metadata: {}
```

Install copies patch files into the backend's patches directory, merges
overrides into `config/custom_configs/config_<name>.yml`, and optionally
writes `patch_config.yml`.
