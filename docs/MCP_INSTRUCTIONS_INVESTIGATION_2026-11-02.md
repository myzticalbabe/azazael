# MCP Instructions Field — Investigation

**Task:** Board 47213 / mcp-instructions-repro
**Date:** 2026-11-02
**Investigator:** opencode lane

## Claim under investigation

"This tree records that its client 'reads mcpServers but discards the MCP initialize
instructions field, so no MCP server can push to the agent'."

## Measurement

Tested two MCP servers by sending an `initialize` request and inspecting the response:

### engram (go binary)
- **Sends instructions:** YES
- **Length:** ~2,500+ characters (full Engram protocol)
- **Content:** Core tools, delivery guarantee, conflict surfacing, session close protocol
- **Protocol compliance:** The `instructions` field is present in the `result` object

### pmb (Python, pams_server_launcher.py)
- **Sends instructions:** NO
- **Response:** `{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"tools":{"listChanged":false}},"serverInfo":{"name":"friday-memory","version":"1.0.0"}}`
- **Protocol compliance:** The `instructions` field is optional per MCP spec, so omitting it is compliant

## Conclusion

1. **The claim "no MCP server can push to the agent" is inaccurate.** engram DOES send
   instructions in its initialize response. The server-side capability exists.

2. **Whether opencode uses the instructions is unverified.** I cannot test opencode's
   client-side behavior from this environment. The claim that opencode "discards" the
   instructions is an assertion about client behavior that needs verification.

3. **pmb does not send instructions.** Even if opencode used them, pmb couldn't push.
   The pmb server would need to add an `instructions` field to its initialize response.

4. **The MCP spec makes instructions optional.** Servers are not required to send them.
   The claim should not imply that all servers should send them.

## Recommendation

- **Revise the claim** to: "opencode's handling of MCP initialize instructions is
  unverified; engram sends them (~2.5K chars) but pmb does not. Whether opencode
  injects them into the system prompt needs a client-side test."
- **Do not file an upstream issue** based on this claim alone. The claim is partially
  inaccurate (engram does send instructions) and the client-side behavior is unverified.
- **Record as a local constraint**: pmb should consider adding an `instructions` field
  to its initialize response for consistency with engram.

## Deliverable checklist

- [x] Reproduced: engram sends instructions, pmb does not
- [x] Claim partially inaccurate (engram does send)
- [x] Client-side behavior unverified (cannot test from here)
- [x] Recommendation: revise claim, don't upstream
- [x] Recorded as local constraint