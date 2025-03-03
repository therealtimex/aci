# Aipolabs Developer Portal

The developer portal for Aipolabs, a platform for developers to manage and configure the apps and functions used by their agents.

## Table of Contents

- [Aipolabs Developer Portal](#aipolabs-developer-portal)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Development Setup](#development-setup)
  - [Linting \& Testing](#linting--testing)
  - [Directory Structure](#directory-structure)
  - [Conventions](#conventions)
  - [Deployment](#deployment)
  - [Additional Links](#additional-links)

## Description

The Dev Portal enables developers to create and manage their projects efficiently. It provides the following key pages for comprehensive project management:

- **Projects Settings**
- **Home Page**
- **App Store Page**
- **App Configurations Page**
- **Account Settings**

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/aipotheosis-labs/aipolabs-dev-portal
   cd aipolabs-dev-portal
   ```

2. **Install dependencies:**
   If you're using npm:

   ```bash
   npm install --legacy-peer-deps
   ```

   (Note: This repo uses Next.js 15, which requires React 19 that is
   [stabilized in Dec 05, 2024](https://react.dev/blog/2024/12/05/react-19).
   Some libraries are stilling upgrading to React 19, so we need to use the
   `--legacy-peer-deps` flag in the mean time.)

3. **Configure Environment Variables:**
   Create a `.env` file with the following variables in it:

   - NEXT_PUBLIC_API_URL: The URL of the Aipolabs backend API server
   - NEXT_PUBLIC_DEV_PORTAL_URL: The URL of the Dev Portal

   You can just set it to the following in local development:

   ```sh
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_DEV_PORTAL_URL=http://localhost:3000
   NEXT_PUBLIC_ENVIRONMENT=local
   ```

4. **Start the application:**

   ```bash
   npm run dev
   ```

## Linting & Testing

This repo uses prettier for formatting, next lint for linting, and vitest for unit tests.

- **Format code:**

  ```bash
  npm run format
  ```

- **Run linters:**

  ```bash
  npm run lint
  ```

- **Run vitest in watch mode:**

  ```bash
  npm run test
  ```

- **Get test coverage:**

  ```bash
  npm run test:coverage
  ```

You can also setup pre-commit hook to run format, lint, and tests when you
commit your code by running (make sure you have [pre-commit](https://pre-commit.com/) installed):

```bash
pre-commit install
```

## Directory Structure

```text
src
├── app (Next.js App Router folder)
│   ├── ... (different pages of the dev portal)
├── components
│   ├── ... (components we created for use in the pages of dev portal)
│   └── ui  (shadcn/ui components we installed)
├── hooks
│   └── use-mobile.tsx
└── lib
│   ├── api          (functions for interacting with the Aipolabs backend API)
│   ├── types        (types of the Aipolabs backend API response)
│   └── utils.ts
└── __test__ (test files, the structure of this folder should be the same as the structure of the src/app folder)
    ├── apps
    ├── linked-accounts
    ├── project-setting
    └── ...
```

## Conventions

- All functions calling the backend API directly should be put in the [src/lib/api](./src/lib/api/) folder.

## Deployment

The Dev Portal is deployed on Vercel: [obnoxiousproxys-projects/aipolabs-dev-portal](https://vercel.com/obnoxiousproxys-projects/aipolabs-dev-portal)

The environment variables need to be set correctly on Vercel: <https://vercel.com/obnoxiousproxys-projects/aipolabs-dev-portal/settings/environment-variables>.

For example, for the Vercel production environment, we set the following environment variables:

```sh
NEXT_PUBLIC_API_URL=https://api.aipolabs.xyz
NEXT_PUBLIC_DEV_PORTAL_URL=https://platform.aipotheosis.xyz
NEXT_PUBLIC_ENVIRONMENT=production
```

## Additional Links

- [Aipolabs Server Repo](https://github.com/aipotheosis-labs/aipolabs)
