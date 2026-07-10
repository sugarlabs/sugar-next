## Purpose

Define Sugar Next's collaboration-first peer layer — the extension-facing
presence hooks, a demonstration link-local peer chat extension, and the
requirement to document transport trade-offs before committing to any
production transport.

## Requirements

### Requirement: Peer presence hooks
The extension API SHALL expose `on_peer_join` and `on_peer_leave` hooks,
called when a peer is discovered or disconnects on the local network.

#### Scenario: Peer discovered
- **WHEN** another Sugar Next instance is discovered on the LAN via
  link-local discovery
- **THEN** installed extensions subscribing to `on_peer_join` are called
  with that peer's id and name

#### Scenario: Peer disconnects
- **WHEN** a previously discovered peer becomes unreachable
- **THEN** installed extensions subscribing to `on_peer_leave` are called
  with that peer's id

### Requirement: Demo P2P chat extension
The shell SHALL ship an example extension demonstrating link-local peer
chat, installed opt-in the same way as the Journal extension.

#### Scenario: Two instances on the same LAN
- **WHEN** two Sugar Next instances with the demo chat extension installed
  are running on the same local network
- **THEN** each discovers the other and can exchange chat messages without
  any account or server configuration

### Requirement: Transport research documented
The project SHALL produce a written comparison of link-local transport
options (XMPP link-local, WebRTC, custom UDP) before any transport is
adopted beyond the demo extension.

#### Scenario: Choosing a transport for future work
- **WHEN** a future change proposes a production collaboration feature
- **THEN** it can reference this comparison instead of re-researching
  transport trade-offs from scratch
