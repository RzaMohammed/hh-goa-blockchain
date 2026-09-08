# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email the maintainers with a detailed description of the issue
3. Include steps to reproduce the vulnerability if possible

## Important Security Notes

- **Never commit your `.env` file** containing private keys or API secrets
- **Never share your Ethereum wallet private key** publicly
- The `.env.example` file contains placeholder values only
- All blockchain transactions on Sepolia testnet use test ETH (no real value)
- SHA-256 hashing is used for content fingerprinting integrity checks
