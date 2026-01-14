# 🎨 Professional Sass Architecture

This project uses a **professional Sass/SCSS architecture** with the **7-1 pattern** for maintainable, scalable stylesheets.

## 📁 Project Structure

```
autonomous-claude/static/scss/
├── abstracts/          # Variables, functions, mixins
│   ├── _variables.scss
│   ├── _functions.scss
│   └── _mixins.scss
├── base/               # Reset, typography, base styles
│   ├── _reset.scss
│   └── _typography.scss
├── components/         # Reusable UI components
│   ├── _buttons.scss
│   ├── _cards.scss
│   ├── _badges.scss
│   ├── _stats.scss
│   ├── _forms.scss
│   ├── _toast.scss
│   └── _code-window.scss
├── layout/            # Major layout components
│   ├── _container.scss
│   ├── _hero.scss
│   ├── _features.scss
│   ├── _tech-stack.scss
│   ├── _workflow.scss
│   ├── _stats.scss
│   ├── _cta.scss
│   ├── _footer.scss
│   ├── _dashboard-header.scss
│   └── _dashboard-layout.scss
└── portfolio.scss     # Main entry point (Portfolio)
└── dashboard.scss     # Main entry point (Dashboard)

multi-agent-system/static/scss/
├── abstracts/
├── base/
├── components/
├── layout/
└── multi-agent.scss   # Main entry point
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Build All CSS Files (Production)

```bash
npm run sass:build
```

This compiles all SCSS files to compressed CSS:
- `portfolio.scss` → `portfolio.css`
- `dashboard.scss` → `style.css`
- `multi-agent.scss` → `style.css`

### 3. Development Mode (Watch Mode)

Watch all files for changes:
```bash
npm run sass:dev
```

Or watch individual projects:
```bash
npm run sass:watch:portfolio      # Portfolio only
npm run sass:watch:dashboard      # Dashboard only
npm run sass:watch:multi-agent    # Multi-agent only
```

## 📦 Available Scripts

| Script | Description |
|--------|-------------|
| `npm run sass:build` | Build all CSS files (compressed, production-ready) |
| `npm run sass:portfolio` | Build portfolio.css only |
| `npm run sass:dashboard` | Build dashboard style.css only |
| `npm run sass:multi-agent` | Build multi-agent style.css only |
| `npm run sass:dev` | Watch all files for changes |
| `npm run sass:watch:portfolio` | Watch portfolio.scss |
| `npm run sass:watch:dashboard` | Watch dashboard.scss |
| `npm run sass:watch:multi-agent` | Watch multi-agent.scss |

## ✨ Features

### 🎯 Professional Architecture
- **7-1 Pattern**: Industry-standard folder structure
- **Modular Components**: Easy to maintain and reuse
- **DRY Principle**: Variables, mixins, and functions reduce repetition

### 🔧 Advanced Sass Features

#### Variables
```scss
// Colors
$primary: #6366f1;
$success: #10b981;

// Spacing
$spacing-md: 12px;
$spacing-lg: 16px;

// Typography
$font-family-base: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

#### Mixins
```scss
// Responsive breakpoints
@include mobile { /* styles */ }
@include tablet { /* styles */ }

// Flexbox utilities
@include flex-center;
@include flex-between;

// Grid layouts
@include grid-columns(3);
@include grid-auto-fit(250px);

// Text gradient
@include text-gradient($gradient-primary);

// Hover effects
@include hover-lift(-10px, $shadow-lg);
```

#### Functions
```scss
// Convert to rem
font-size: rem(16);

// Add alpha to colors
background: alpha($primary, 0.2);

// Color manipulation
color: lighten-color($primary, 10%);
color: darken-color($primary, 10%);
```

### 🎨 Component System

All UI components are modular and reusable:
- **Buttons**: Primary, secondary, large variants
- **Cards**: Feature cards, stat cards, workflow steps
- **Forms**: Inputs, textareas with focus states
- **Stats**: Grids, bars, metrics
- **Toast**: Notification system
- **Badges**: Status indicators

### 📱 Responsive Design

Built-in responsive mixins:
```scss
.hero {
  grid-template-columns: 1fr 1fr;

  @include tablet {
    grid-template-columns: 1fr;
  }

  @include mobile {
    padding: 20px;
  }
}
```

### 🎭 Animations

Keyframe animations included:
- `pulse` - Pulsing effect
- `fadeInDown` - Fade in from top
- `fadeInUp` - Fade in from bottom
- `slideInRight` - Slide in from right
- `spin` - Loading spinner

## 🛠️ Customization

### Changing Colors

Edit `abstracts/_variables.scss`:
```scss
$primary: #your-color;
$success: #your-color;
```

### Adding New Components

1. Create new file in `components/`:
   ```scss
   // components/_my-component.scss
   .my-component {
     // styles
   }
   ```

2. Import in main file:
   ```scss
   @import 'components/my-component';
   ```

### Creating New Mixins

Add to `abstracts/_mixins.scss`:
```scss
@mixin my-mixin($param) {
  // styles
}
```

## 📊 File Sizes

**Before Sass (Original CSS):**
- portfolio.css: 552 lines
- style.css (dashboard): 534 lines
- style.css (multi-agent): 373 lines

**After Sass (Modular):**
- 40+ partial files
- Better organization
- Easier maintenance
- Compressed production builds

## 🎓 Learning Resources

- [Sass Documentation](https://sass-lang.com/documentation)
- [7-1 Pattern](https://sass-guidelin.es/#the-7-1-pattern)
- [Sass Guidelines](https://sass-guidelin.es/)

## 📝 Best Practices

1. **Use variables** for all colors, spacing, and typography
2. **Create mixins** for repeated patterns
3. **Keep components small** and focused
4. **Use nesting** wisely (max 3-4 levels)
5. **Prefix partials** with underscore (_variables.scss)
6. **Comment your code** when necessary
7. **Test responsive** breakpoints

## 🔄 Workflow

1. Make changes to `.scss` files
2. Run `npm run sass:dev` in development
3. Files auto-compile on save
4. Build production with `npm run sass:build`
5. Commit both SCSS and compiled CSS

---

**Made with** 💜 **using Professional Sass Architecture**
