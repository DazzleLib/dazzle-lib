# Platform Support

dazzle-lib contains **types only** (Protocols, TypedDicts, exceptions, one
formatting mixin) -- no I/O, no platform probing, no conditional code paths.
Platform behavior is therefore uniform by construction.

| Platform | Status | Notes |
|---|---|---|
| Windows | Tested | Primary development platform |
| Linux | Expected to work | No platform-specific code exists to diverge |
| macOS | Expected to work | No platform-specific code exists to diverge |
| BSD | Expected to work | No platform-specific code exists to diverge |

| Python | Status |
|---|---|
| 3.9 -- 3.13 | Supported (`typing.Protocol`/`TypedDict` are 3.8+ features; floor set at 3.9 to match the stack) |

The only platform-RELEVANT content is documentation: `TimestampsDict.created`
carries `st_ctime`, which means creation time on Windows but inode-change time
on Unix -- the schema documents this so consumers don't assume birth-time
semantics cross-platform.
