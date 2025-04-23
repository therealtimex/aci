# Contributing to ACI.dev

Thank you for your interest in contributing to ACI.dev! We welcome contributions from everyone, whether it's submitting bug reports, suggesting new features, improving documentation, or contributing code.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an open and welcoming community.

## Getting Started

Before you begin contributing, please set up your local development environment by following the instructions in the [README.md](README.md).

## Contributor License Agreement (CLA)

Before we can merge your contribution, we need you to agree to our Contributor License Agreement (CLA). This protects both you and the project.

- **Individuals:** Please read the [Individual CLA (CLA-Individual.md)](CLA-Individual.md). To signify your agreement, comment on your Pull Request with the exact phrase:
    `I have read the CLA Document and I hereby sign the CLA`

- **Corporations:** If you are contributing on behalf of a company, please ensure **both** of the following steps are completed:
    1. An authorized representative from your company must read the [Corporate CLA (CLA-Corporate.md)](CLA-Corporate.md) and signify agreement by commenting on the Pull Request with the exact phrase: `We have read the CLA Document and we hereby sign the CLA`. This comment must also include the Corporation Name, Address, Point of Contact Name, Email, and Phone number as specified in the Corporate CLA.
    2. The individual developer submitting the code must **also** sign the [Individual CLA (CLA-Individual.md)](CLA-Individual.md) by commenting with the phrase specified in the "Individuals" section above.

We cannot accept pull requests until **all** required CLA agreements are met.

## Repository Structure

Our monorepo contains two main components:

- **`/backend`**: Contains the main ACI platform server, including the APIs, core logic, database models, and the entire integration library (over 600+ tools).
- **`/frontend`**: Contains the Next.js application for the ACI.dev Developer Portal. This is the web interface for managing projects, integrations, authentication, and testing agents.

## Getting in Touch

Before starting work on a contribution, especially for larger features or changes, we kindly request that you first get in touch with the core team by emailing <support@aipolabs.xyz>. This helps us coordinate efforts, provide guidance, and ensure your contribution aligns with the project's roadmap.

## How to Contribute

### Reporting Bugs

If you've found a bug:

1. Check if the bug has already been reported in the GitHub Issues
2. If not, create a new issue with a clear title and description
3. Include steps to reproduce, expected behavior, and actual behavior
4. Add any relevant screenshots or error logs

### Suggesting Features

We welcome feature suggestions:

1. Describe the feature and its use case
2. Explain how it would benefit ACI.dev users
3. Provide any examples or references if available

### Code Contributions

1. **Fork the repository** to your GitHub account
2. **Clone your fork** to your local machine
3. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes** following our coding standards (see below)
5. **Commit your changes** with clear, descriptive commit messages and make sure all commit hooks pass
6. **Push your branch** to your fork
7. **Create a pull request** to the main repository

#### Pull Request Process

1. Ensure your code follows our coding standards
2. Update documentation if necessary
3. Make sure all tests pass
4. Reference any related issues in your pull request description
5. Wait until all CI checks are green
6. Request a review from a maintainer

## Coding Standards

Check out the README file for each component for more information on coding standards.

- **Backend:** [backend/README.md](backend/README.md)
- **Frontend:** [frontend/README.md](frontend/README.md)

## Testing

Check out the README file for each component for more information on testing.

- **Backend:** [backend/README.md](backend/README.md)
- **Frontend:** [frontend/README.md](frontend/README.md)

## License

By contributing to ACI.dev, you agree that your contributions will be licensed under the project's [Apache 2.0 License](LICENSE).
