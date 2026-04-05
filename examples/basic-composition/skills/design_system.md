---
name: Design System Engineer
description: Building and maintaining UI components, design tokens, and accessibility standards for a consistent design system using Tailwind CSS and React.
capabilities: [design, components, tailwind, accessibility, tokens, react, ui]
version: "1.0"
author: Weave Example
---

# Design System Engineer

This skill governs how UI components, design tokens, and visual standards are implemented and maintained across the product. Every component must be token-driven, accessible, and consistent with the design system.

## Component Structure

- Use functional React components with named exports only. No default exports.
- Accept a `className` prop on every presentational component for consumer overrides.
- Keep components under 150 lines. Extract sub-components when a component grows larger.
- Co-locate the component, its types, and its tests in the same directory.

## Design Tokens

- Never hardcode colours, spacing, or typography values directly in components.
- Use Tailwind design tokens exclusively: `text-primary`, `bg-surface`, `p-4`.
- Custom tokens live in `tailwind.config.js` under `theme.extend`. Never duplicate them.
- When a token does not exist, propose adding it — do not use a raw value as a workaround.

## Accessibility

- Every interactive element must be keyboard-navigable with a visible focus ring.
- Use semantic HTML: `<button>` not `<div onClick>`, `<nav>` not `<div className="nav">`.
- All images require `alt` text. Purely decorative images use `alt=""`.
- Colour contrast must meet WCAG AA minimums: 4.5:1 for normal text, 3:1 for large text.

## Naming Conventions

- Component files: PascalCase (`ButtonGroup.tsx`, `CardHeader.tsx`).
- CSS class variables: kebab-case (`--color-primary`, `--spacing-base`).
- Props: camelCase, descriptive (`isDisabled` not `dis`, `onValueChange` not `onChange2`).
