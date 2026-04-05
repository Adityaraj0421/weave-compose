---
name: Naksha Design System
description: UI component design and design system implementation for React applications using Tailwind CSS. Handles visual hierarchy, spacing, typography, color tokens, and Figma-to-code workflows.
capabilities:
  - design
  - components
  - ui
  - tailwind
  - figma
  - typography
  - spacing
  - color
  - layout
  - react
version: "1.0"
author: Naksha Studio
---

# Naksha Design System

This skill handles UI component design, design system implementation, and visual design decisions for React applications. Use it when building components, implementing Figma designs in code, or establishing a consistent design language.

## When to Use

- Building reusable UI components (buttons, cards, modals, forms)
- Translating Figma designs into React + Tailwind CSS code
- Setting up or extending a design system
- Defining spacing, typography, or color tokens
- Reviewing components for visual consistency and accessibility
- Creating responsive layouts and grid systems

## Core Design Principles

- **Consistency first.** Every spacing value, color, and font size must come from the design token system. Never use arbitrary values.
- **Accessibility by default.** Color contrast must meet WCAG AA (4.5:1 for text). All interactive elements need focus states.
- **Mobile-first responsive design.** Start with the smallest breakpoint and scale up using Tailwind's `sm:`, `md:`, `lg:` prefixes.
- **Semantic HTML.** Use the correct element for the job (`button` not `div`, `nav` not `div`, `h1`–`h6` in order).
- **Visual hierarchy.** Guide the user's eye through size, weight, color, and spacing — not decoration.

## Component Rules

- Use Tailwind utility classes — no inline styles, no CSS modules for new components
- All colors from the design token palette (`primary`, `secondary`, `neutral`, `error`, `success`)
- Spacing from the 4px base grid: `p-1`=4px, `p-2`=8px, `p-4`=16px, `p-6`=24px, `p-8`=32px
- Font sizes: `text-xs` (12px), `text-sm` (14px), `text-base` (16px), `text-lg` (18px), `text-xl` (20px), `text-2xl` (24px)
- Components must accept a `className` prop for composition
- Export components as named exports, never default exports

## File Structure

```
components/
  Button/
    Button.tsx        # Component implementation
    Button.stories.tsx # Storybook stories
    index.ts          # Re-export
```

## Design Review Checklist

- [ ] Spacing follows the 4px grid
- [ ] Colors use design tokens only
- [ ] Accessible contrast ratios verified
- [ ] Component works at all breakpoints
- [ ] Focus states visible and styled
