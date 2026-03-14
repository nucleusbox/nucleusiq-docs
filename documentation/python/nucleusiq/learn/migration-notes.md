# Migration Notes

## From simpler chat wrappers

- Move from `prompt -> response` to `Agent + Task`
- Introduce tools gradually in STANDARD mode
- Use usage tracking to prevent cost surprises

## From heavier workflow systems

- Start with one Agent + STANDARD mode
- Add plugins for policy and retries
- Introduce AUTONOMOUS only where verification loops are needed
