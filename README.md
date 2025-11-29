# BETTI - Base Event Token Time Intent

Physics-based intent coordination framework with Humotica context.

## Installation

```bash
pip install betti
```

## Quick Start

```python
from betti import BETTIClient, TIBET, Humotica

# Create client
client = BETTIClient('http://localhost:8081', secret='your_secret_here')

# Build intent with human context
intent = TIBET.intent('turn_on_lights') \
    .with_humotica(Humotica()
        .purpose('User arriving home')
        .context('Evening, dark outside')
        .emotional_state('tired from work')) \
    .build()

# Execute
result = client.execute(intent)
```

## Documentation

- [Getting Started](docs/getting-started/)
- [Architecture](docs/architecture/)
- [14 Physics Laws](papers/14-PHYSICS-LAWS.md)
- [Humotica Framework](humotica/)

## Requires

- [JIS Protocol](https://github.com/jaspertvdm/JTel-identity-standard) for identity & trust

## License

JOSL - See [LICENSE.md](LICENSE.md)

