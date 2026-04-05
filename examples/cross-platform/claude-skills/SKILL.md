---
name: React Component Library
description: Building and maintaining reusable React components with design tokens, accessibility compliance, and Storybook documentation for a shared component library.
capabilities: [react, components, design-tokens, accessibility, storybook, typescript]
version: "1.0"
author: Weave Example
---

# React Component Library

This skill governs how components are built, documented, and maintained in the shared component library. Every component must be accessible, token-driven, and accompanied by a Storybook story.

## Component Authoring

- Use functional components with named exports only. Never use default exports.
- Accept a `className` prop on every presentational component for consumer overrides.
- Keep components under 150 lines. Extract sub-components if a component grows larger.
- Co-locate the component, its types, its tests, and its story in the same directory.

## Design Tokens

- Never hardcode colours, spacing, or font sizes. Always reference design tokens.
- Use CSS custom properties (`--color-primary`, `--spacing-4`) — not raw hex values.
- Token values live in `src/tokens/`. Never duplicate token definitions across files.

## Accessibility

- Every interactive component must be keyboard-navigable with a visible focus ring.
- Use semantic HTML: `<button>` not `<div onClick>`, `<nav>` not `<div role="navigation">`.
- All images require `alt` text. Decorative images use `alt=""`.
- Run `axe` accessibility checks in Storybook on every component story.

## Storybook

- Every component must have at least one story: Default, and one per meaningful variant.
- Stories must use `args` and `argTypes` — no hardcoded props inside story functions.
- Document all props in the `argTypes` block with descriptions and control types.
