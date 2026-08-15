# Skill: frontend-ui-ux

## Purpose
Defines the mandatory high-level UI/UX design guidelines to prevent generic, "cookie-cutter" or "AI-slop" interfaces. This skill ensures a distinctive, cohesive, and visually engaging user experience for the Biblioteca Virtual Inteligente.

## When to Apply
- MUST be applied ALWAYS when the `@frontend-developer` role implements or modifies any UI component, page, or layout.
- MUST be considered during the planning phase (`plan-user-story`) when defining frontend tasks.

## Core Rules (Mandatory)

### 1. Typography
- **Requirement:** Use distinctive, intentional fonts.
- **AVOID (Strictly Prohibited):** Inter, Roboto, Arial, System Fonts, Space Grotesk.
- **Action:** Select unique typefaces that match the "Biblioteca" (Library) theme (e.g., elegant serifs for headings, clean but distinct sans-serifs for body).

### 2. Color Palette
- **Requirement:** Build a cohesive, structured palette using CSS variables.
- **AVOID (Strictly Prohibited):** Purple gradients on white backgrounds (commonly associated with "AI slop").
- **Action:** Use a deliberate color system with primary, secondary, accent, and neutral tones. Consider warm or earthy tones (e.g., deep greens, terracotta, warm ivories, golds) that evoke the feeling of a physical library.

### 3. Motion & Animation
- **Requirement:** Implement orchestrated page load flows with staggered reveals.
- **Preference:** CSS-only animations are preferred over JavaScript-heavy libraries for performance.
- **Action:** Elements should fade, slide, or scale in sequentially (e.g., header → main content → sidebar) to create a polished, premium feel rather than a static, blocky page.

### 4. Spatial Composition
- **Requirement:** Utilize unexpected, dynamic layouts.
- **Avoid:** Predictable, perfectly symmetrical grid-only layouts.
- **Action:** Introduce asymmetry, overlapping elements, diagonal flows, or broken grid layouts. The design should feel intentional and editorial, not purely algorithmic.

### 5. Visual Details & Textures
- **Requirement:** Add rich, tactile visual details.
- **AVOID (Strictly Prohibited):** Flat, solid colors without texture.
- **Action:** Use subtle grain overlays, soft shadows, gradients (not purple/white), and noise textures to add depth. The interface should feel tangible and warm.

### 6. Anti-Patterns (Never Do)
- **Generic Fonts:** Do not use default browser fonts.
- **Cliché Colors:** Do not use the standard "AI" color schemes (purple/white/teal).
- **Predictable Layouts:** Do not use standard centered-cards-in-a-row patterns exclusively.
- **Cookie-Cutter Design:** Do not reproduce standard shadcn/ui templates without custom styling (colors, spacing, typography) that aligns with these rules.

## Implementation Checklist
When implementing a UI component or page:
1. [ ] Are the fonts distinctive and non-generic?
2. [ ] Is the color palette cohesive and free of "AI-slop" combinations?
3. [ ] Is there a sequence of staggered reveals or smooth transitions?
4. [ ] Does the layout break away from predictable symmetry?
5. [ ] Are textures, shadows, or grain overlays applied to add depth?

## Documentation Requirement
The `@frontend-developer` MUST document the aesthetic direction (fonts chosen, primary colors, inspiration) in the Pull Request description or the story's `Implementation Notes` for every feature delivered.
