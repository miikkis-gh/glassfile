# Glassmorphic File Manager

## Project Overview
A **stunning**, secure file hosting solution featuring an Apple-inspired glassmorphism web interface and CLI management tools. Designed for self-hosted file sharing with direct download links accessible via wget.

This project prioritizes **exceptional visual design** with a premium dark mode aesthetic, smooth animations, and an immersive user experience that rivals commercial products.

## Purpose
Host files on a personal Debian server with:
- **Public Access**: Direct download links for files (wget-compatible)
- **Secure Management**: Password-protected web interface and CLI tools
- **Beautiful UI**: Premium glassmorphism design that sets a new standard for self-hosted tools

## Architecture

### Components
1. **Web Server** (Python Flask)
   - Serves static files for direct downloads
   - Hosts glassmorphic management interface
   - REST API for file operations
   - Session-based authentication for web UI
   - API key authentication for CLI

2. **Web Interface** (HTML/CSS/JS)
   - Apple-inspired glassmorphism design
   - Animated gradient background with floating blobs
   - File upload, delete, rename, and list operations
   - Responsive design (mobile, tablet, desktop)
   - Accessibility features

3. **CLI Manager** (Python)
   - Command-line tool for file operations
   - API key authentication
   - Operations: upload, download, delete, list, rename

4. **Storage**
   - Files stored in organized directory structure
   - Direct URL access: `http://server/files/filename.ext`

## Design Specifications

### Core Design Philosophy
This interface should feel like a **premium Apple product** - polished, elegant, and delightful to use. Every interaction should be smooth, every animation purposeful, and every detail considered.

### Visual Design System

#### Glassmorphism Implementation
- **Backdrop Blur**: Use `backdrop-filter: blur(20px)` for primary surfaces
- **Translucent Backgrounds**: RGBA colors with 10-15% opacity (e.g., `rgba(255, 255, 255, 0.1)`)
- **Subtle Borders**: 1px borders with `rgba(255, 255, 255, 0.2)` to define edges
- **Layering**: Multiple glass layers create depth hierarchy
- **Shadows**: Soft, colored shadows that complement the gradient background

#### Typography
- **Font Family**: Inter (load from Google Fonts)
- **Weights**: 
  - Regular (400) for body text
  - Medium (500) for labels
  - Semibold (600) for headings
  - Bold (700) for emphasis
- **Sizes**: 
  - Headings: 2rem - 3rem
  - Body: 0.875rem - 1rem
  - Small: 0.75rem
- **Line Height**: 1.5 for readability
- **Letter Spacing**: -0.02em for headings (tighter), 0 for body

#### Color Palette
**Primary Dark Background**: `#0a0a0f` (deep near-black)

**Gradient Blob Colors**:
- Indigo: `#6366f1` → `#4f46e5`
- Violet: `#8b5cf6` → `#7c3aed`
- Sky: `#0ea5e9` → `#0284c7`
- Cyan: `#06b6d4` → `#0891b2`
- Fuchsia: `#d946ef` → `#c026d3`

**Glass Surface Colors**:
- Primary glass: `rgba(255, 255, 255, 0.1)`
- Hover glass: `rgba(255, 255, 255, 0.15)`
- Active glass: `rgba(255, 255, 255, 0.2)`

**Text Colors**:
- Primary: `rgba(255, 255, 255, 0.95)`
- Secondary: `rgba(255, 255, 255, 0.7)`
- Tertiary: `rgba(255, 255, 255, 0.5)`

**Border Colors**:
- Subtle: `rgba(255, 255, 255, 0.1)`
- Defined: `rgba(255, 255, 255, 0.2)`
- Strong: `rgba(255, 255, 255, 0.3)`

### Background Animation System

#### Gradient Mesh (5 Floating Blobs)
Each blob must be implemented as a CSS element with:
- **Size**: 400-600px diameter (varies per blob)
- **Shape**: Perfect circles with heavy blur (150-200px)
- **Colors**: See gradient blob colors above
- **Positioning**: Absolute, distributed across viewport
- **Z-index**: Behind all content (-1)

**Animation Requirements**:
1. **Organic Continuous Motion**:
   - Each blob follows a unique path using CSS `@keyframes`
   - Duration: 20-30 seconds per cycle (different for each)
   - Easing: `cubic-bezier(0.4, 0.0, 0.2, 1)` for smooth motion
   - Alternate direction for seamless loops
   - Movement: Translate X and Y by 10-20% viewport size

2. **Mouse Parallax Effect**:
   - Track mouse position using JavaScript
   - Apply subtle translation to blobs (5-15px range)
   - Use `transform: translate3d()` for GPU acceleration
   - Smooth easing with `transition: transform 0.5s ease-out`
   - Each blob moves at different speed (layered depth effect)

3. **Noise Texture Overlay**:
   - Create SVG noise filter or use CSS grain effect
   - Opacity: 3-5% for subtle texture
   - Fixed position covering entire viewport
   - Z-index: Above blobs, below content

**Implementation Example Structure**:
```html
<div class="background">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>
  <div class="blob blob-4"></div>
  <div class="blob blob-5"></div>
  <div class="noise-overlay"></div>
</div>
```

### Button Component System

Every interactive button (upload, delete, rename, logout, etc.) must follow this exact specification:

#### Structure
```html
<button class="glass-button">
  <svg class="button-icon">[icon]</svg>
  <span class="button-text">Button Text</span>
  <svg class="button-arrow">[arrow]</svg>
</button>
```

#### Visual Treatment
1. **Base State**:
   - Background: `rgba(255, 255, 255, 0.1)`
   - Border: `1px solid rgba(255, 255, 255, 0.2)`
   - Backdrop blur: `blur(20px)`
   - Padding: `12px 24px`
   - Border radius: `12px`
   - Font: Inter Medium, 0.875rem
   - Box shadow: `0 8px 32px rgba(0, 0, 0, 0.3)`

2. **Hover State** (smooth transitions):
   - **Lift Effect**: `transform: translateY(-2px)`
   - **Enhanced Glow**: Add colored shadow matching context (e.g., upload button gets cyan glow)
     - Example: `box-shadow: 0 8px 32px rgba(6, 182, 212, 0.4), 0 0 40px rgba(6, 182, 212, 0.2)`
   - **Brightness Increase**: Background becomes `rgba(255, 255, 255, 0.15)`
   - **Arrow Reveal**: Arrow slides in from right using `transform: translateX()`
     - Initial: `translateX(-8px)` and `opacity: 0`
     - Hover: `translateX(0)` and `opacity: 1`

3. **Active/Focus States**:
   - Focus: 2px outline with `outline: 2px solid rgba(99, 102, 241, 0.5)` and `outline-offset: 2px`
   - Active: Slight scale down `transform: scale(0.98)`

4. **Icon Styling**:
   - Size: 20x20px
   - Color: Current text color
   - Margin right: 8px
   - Must be custom SVG paths (see icon library below)

5. **Transition Timing**:
   - All transitions: `0.3s cubic-bezier(0.4, 0.0, 0.2, 1)`
   - Arrow slide: `0.3s cubic-bezier(0.34, 1.56, 0.64, 1)` (bounce effect)

#### SVG Icon Library
Create inline SVG icons for:
- **Upload**: Cloud with upward arrow
- **Delete**: Trash can
- **Rename**: Pencil/edit icon
- **Download**: Downward arrow to tray
- **Copy**: Two overlapping rectangles
- **Logout**: Exit door with arrow
- **Arrow**: Right-pointing chevron (for button reveals)

Each icon should be:
- 24x24 viewBox
- 2px stroke width
- Rounded line caps and joins
- Single color (currentColor)

### Animation System

#### Staggered Entrance Animations
All major UI elements (heading, buttons, file cards) should animate in on page load:

1. **Timing**: Each element delays by 0.1s from previous
2. **Effect**: Fade in + slide up
   - Initial: `opacity: 0`, `transform: translateY(20px)`
   - Final: `opacity: 1`, `transform: translateY(0)`
3. **Duration**: 0.6s per element
4. **Easing**: `cubic-bezier(0.4, 0.0, 0.2, 1)`

**Implementation**:
```css
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeSlideUp 0.6s cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
}

.animate-in:nth-child(1) { animation-delay: 0.1s; }
.animate-in:nth-child(2) { animation-delay: 0.2s; }
/* etc. */
```

#### Micro-interactions
- File cards: Scale up slightly on hover (1.02)
- Delete button: Shake animation on click
- Copy link: Ripple effect + "Copied!" tooltip
- Upload zone: Pulse border when dragging file over

### Responsive Design Breakpoints

#### Mobile (< 640px)
- Single column layout
- Blobs scale down (300-400px)
- Reduced blur amounts (10px instead of 20px)
- Larger touch targets (44x44px minimum)
- Simplified animations (reduce motion)
- Stack buttons vertically

#### Tablet (640px - 1024px)
- Two column file grid
- Medium-sized blobs (400-500px)
- Maintain all animations
- Adjusted spacing

#### Desktop (> 1024px)
- Three column file grid
- Full-sized blobs (400-600px)
- Full parallax effect
- Maximum visual fidelity

**Media Query Structure**:
```css
/* Mobile first base styles */

@media (min-width: 640px) {
  /* Tablet styles */
}

@media (min-width: 1024px) {
  /* Desktop styles */
}
```

### Accessibility Requirements

#### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Logical tab order
- Visible focus indicators (outlined glass effect)
- Skip to content link
- Escape key to close modals/dialogs

#### Focus States
- 2px outline in accent color
- 2px offset from element
- High contrast in high contrast mode
- Never use `outline: none` without replacement

#### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  /* Keep blobs static */
  .blob {
    animation: none;
  }
}
```

#### High Contrast Mode
```css
@media (prefers-contrast: high) {
  .glass-button {
    border-width: 2px;
    background: rgba(255, 255, 255, 0.2);
  }
}
```

#### ARIA Labels
- All buttons: `aria-label` describing action
- Upload zone: `role="button"` and `aria-label="Upload files"`
- File list: `role="list"` with `role="listitem"` children
- Modals: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`

#### Screen Reader Support
- Semantic HTML5 elements
- Descriptive link text (no "click here")
- Status announcements for actions (upload complete, file deleted)
- Alternative text for all non-decorative images

### Layout Structure

#### Main Interface Components

1. **Header Section** (glassmorphic)
   - App title/logo
   - User indicator
   - Logout button (top right)

2. **Action Bar** (glassmorphic, staggered animation)
   - Upload button (primary, cyan glow)
   - Refresh list button
   - Storage usage indicator (optional)

3. **File Grid** (responsive columns)
   - Each file: glassmorphic card
   - File icon, name, size, date
   - Actions: Download, Copy Link, Rename, Delete
   - Hover effect: lift + glow
   - Empty state: Beautiful centered message

4. **Upload Modal** (glassmorphic overlay)
   - Drag-and-drop zone
   - Or click to browse
   - Progress indicator
   - Cancel button

5. **Login Screen** (separate page)
   - Centered glassmorphic card
   - Password input
   - Login button
   - Same animated background

### File Card Design
```
┌──────────────────────────────────┐
│  📄  filename.pdf                │
│                                  │
│  2.4 MB • 2 hours ago           │
│                                  │
│  [Download] [Copy] [⋯ More]     │
└──────────────────────────────────┘
```

- Glass background
- Hover: lift + cyan glow
- Smooth transitions
- Three-dot menu for rename/delete

## Security Model

### Public File Access
- Files in `/files/` directory are publicly accessible
- Direct URLs for wget downloads
- No authentication required for downloads

### Management Access
- Web interface: Session-based authentication with password
- CLI tool: API key authentication
- Credentials stored in `config.yaml`
- Optional IP whitelist capability

## Technology Stack
- **Backend**: Python 3.8+ with Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks needed - keep it pure and performant)
- **Fonts**: Inter from Google Fonts (weights: 400, 500, 600, 700)
- **Storage**: Local filesystem
- **Deployment**: Systemd service with optional Nginx reverse proxy
- **Security**: werkzeug for password hashing, secrets for API keys

## File Structure
```
/home/claude/
├── fileserver.py          # Main Flask application
├── filemanager            # CLI management tool (executable)
├── config.yaml            # Configuration file
├── templates/
│   ├── index.html         # Main glassmorphic interface
│   └── login.html         # Login page (same design)
├── static/
│   └── files/             # Public file storage directory
├── fileserver.service     # Systemd service file
├── nginx.conf.example     # Nginx reverse proxy config
├── CLAUDE.md             # This file
├── MILESTONES.md         # Development milestones
└── README.md             # User documentation
```

## Critical Implementation Notes

### CSS Architecture
Use CSS Custom Properties for the entire design system:
```css
:root {
  /* Colors */
  --color-background: #0a0a0f;
  --color-text-primary: rgba(255, 255, 255, 0.95);
  --color-text-secondary: rgba(255, 255, 255, 0.7);
  --color-glass-bg: rgba(255, 255, 255, 0.1);
  --color-glass-border: rgba(255, 255, 255, 0.2);
  
  /* Gradient blob colors */
  --color-blob-indigo: #6366f1;
  --color-blob-violet: #8b5cf6;
  --color-blob-sky: #0ea5e9;
  --color-blob-cyan: #06b6d4;
  --color-blob-fuchsia: #d946ef;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Blur amounts */
  --blur-sm: 10px;
  --blur-md: 20px;
  --blur-lg: 30px;
  
  /* Border radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  
  /* Transitions */
  --transition-fast: 0.15s cubic-bezier(0.4, 0.0, 0.2, 1);
  --transition-normal: 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
  --transition-slow: 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

### JavaScript Requirements

#### Mouse Parallax Implementation
```javascript
// Track mouse position
let mouseX = 0, mouseY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = (e.clientX / window.innerWidth) * 2 - 1;
  mouseY = (e.clientY / window.innerHeight) * 2 - 1;
  updateBlobPositions();
});

function updateBlobPositions() {
  // Apply different multipliers for depth
  const blobs = document.querySelectorAll('.blob');
  blobs.forEach((blob, index) => {
    const depth = (index + 1) * 5; // 5px, 10px, 15px, etc.
    blob.style.transform = `translate(${mouseX * depth}px, ${mouseY * depth}px)`;
  });
}
```

#### Staggered Animation on Load
```javascript
// Add animate-in class with delays
window.addEventListener('DOMContentLoaded', () => {
  const elements = document.querySelectorAll('.animate-on-load');
  elements.forEach((el, index) => {
    el.style.animationDelay = `${index * 0.1}s`;
    el.classList.add('animate-in');
  });
});
```

#### File Upload with Drag-and-Drop
```javascript
// Implement drag-and-drop for upload zone
const dropZone = document.getElementById('upload-zone');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const files = e.dataTransfer.files;
  handleFileUpload(files);
});
```

### Performance Optimization

1. **GPU Acceleration**: Use `transform: translate3d()` for all animations
2. **Will-change**: Apply to animated elements: `will-change: transform, opacity`
3. **Backdrop Filter Optimization**: Limit to necessary elements only
4. **Debounce Parallax**: Update positions max 60fps
5. **Lazy Load**: Load file list progressively if > 50 files

### Browser Compatibility
- **Target Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Backdrop Filter Support**: Check and provide fallback
- **CSS Grid**: Primary layout method
- **Flexbox**: For component internals

### Security Considerations in Frontend
- Sanitize file names before display (prevent XSS)
- Validate file types on upload
- Show loading states to prevent double-submission
- Display file size limits clearly
- Implement rate limiting feedback

## Flask Application Structure

### Required Routes

#### Authentication
- `GET /login` - Login page
- `POST /login` - Login submission (JSON)
- `GET /logout` - Clear session and redirect

#### Web Interface (requires login)
- `GET /` - Main interface (or redirect to login)
- `GET /api/files` - List all files (JSON)
- `POST /api/upload` - Upload file
- `DELETE /api/files/<filename>` - Delete file
- `PUT /api/files/<filename>` - Rename file
- `GET /api/files/<filename>/info` - Get file metadata

#### Public Access (no auth)
- `GET /files/<filename>` - Download file (wget-compatible)

#### CLI API (requires API key header)
- Same as web API but checks `X-API-Key` header

### Response Format
All API responses should be JSON:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Or on error:
```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

### Session Management
- Use Flask sessions with secure cookie
- Set session lifetime from config
- Regenerate session ID on login
- Clear session completely on logout

## CLI Tool Requirements

### Command Structure
```bash
./filemanager <command> [options]

Commands:
  list                    List all files
  upload <file>          Upload a file
  delete <filename>      Delete a file
  rename <old> <new>     Rename a file
  info <filename>        Show file details
  config                 Show current configuration
  set-api-key <key>      Set API key for authentication
```

### Features
- Colorful terminal output (use ANSI codes)
- Progress bar for uploads (use tqdm or custom)
- Confirmation prompts for destructive actions
- Store API key in `~/.filemanager.conf`
- Display file sizes in human-readable format
- Show relative timestamps (e.g., "2 hours ago")

### Error Handling
- Network errors: Retry with exponential backoff
- Authentication errors: Clear stored key, prompt for new one
- File not found: Clear error message
- Connection refused: Suggest checking if server is running

## Configuration File Format

### config.yaml Structure
```yaml
server:
  host: '0.0.0.0'
  port: 8080
  debug: false

storage:
  directory: './static/files'
  max_file_size: 104857600  # 100MB in bytes
  allowed_extensions: null   # null = all allowed, or list: ['.pdf', '.jpg']

security:
  admin_password_hash: 'pbkdf2:sha256:...'  # Generated by werkzeug
  api_keys:
    - 'your-secure-api-key-here'
  session_lifetime: 3600  # seconds
  ip_whitelist: []        # Empty = all allowed, or ['192.168.1.1', ...]

display:
  files_per_page: 50      # For pagination
  date_format: 'relative' # 'relative' or 'absolute'
```

## Development Workflow for Claude Code

### Phase 1: Backend Foundation
1. Create `fileserver.py` with Flask app structure
2. Implement all routes with placeholder responses
3. Add authentication decorators
4. Create config loading system
5. Test with curl commands

### Phase 2: Stunning Frontend
1. Create `templates/login.html` with glassmorphism design
   - Implement animated background with 5 blobs
   - Add noise overlay
   - Create centered login card
   - Test responsiveness

2. Create `templates/index.html` with full interface
   - Same animated background system
   - Header with app title and logout button
   - Action bar with upload and refresh buttons
   - File grid with glassmorphic cards
   - Upload modal with drag-and-drop
   - All button components with icons and arrow reveals
   - Implement mouse parallax
   - Add staggered entrance animations
   - Test all breakpoints

3. Add JavaScript functionality
   - File list loading
   - Upload with progress
   - Delete with confirmation
   - Rename modal
   - Copy link to clipboard
   - Handle all edge cases

### Phase 3: CLI Tool
1. Create `filemanager` Python script with argparse
2. Implement all commands
3. Add progress indicators
4. Test against running server
5. Make executable (`chmod +x`)

### Phase 4: Production Readiness
1. Create `fileserver.service` for systemd
2. Create `nginx.conf.example` for reverse proxy
3. Write comprehensive `README.md`
4. Add security hardening notes
5. Create installation script

### Phase 5: Testing & Polish
1. Test all features end-to-end
2. Verify animations at 60fps
3. Test on mobile devices
4. Accessibility audit with keyboard navigation
5. Test with screen reader
6. Cross-browser testing
7. Security audit

## Quality Standards

### Code Quality
- **Python**: Follow PEP 8, use type hints
- **HTML**: Semantic HTML5, proper nesting
- **CSS**: Organized by component, consistent naming
- **JavaScript**: Modern ES6+, clear function names
- **Comments**: Explain "why", not "what"

### Visual Quality
- **Animations**: Smooth 60fps, no jank
- **Spacing**: Consistent throughout
- **Alignment**: Pixel-perfect
- **Colors**: Exact gradient values
- **Typography**: Proper hierarchy

### UX Quality
- **Loading States**: Show for every async action
- **Error Messages**: Clear and actionable
- **Success Feedback**: Confirm completed actions
- **Empty States**: Beautiful and helpful
- **Responsiveness**: Instant feeling interactions

## Success Criteria

The project is complete when:

✅ **Visual Excellence**
- Background blobs animate smoothly with parallax
- All buttons have glass effect with hover animations
- Staggered entrance animations work perfectly
- Design is pixel-perfect on all screen sizes
- Reduced motion preferences are respected

✅ **Functionality**
- Files can be uploaded via web interface and CLI
- Files can be downloaded via direct wget links
- Files can be renamed and deleted
- Authentication works for web and CLI
- All edge cases handled gracefully

✅ **Accessibility**
- Full keyboard navigation works
- Screen reader compatible
- High contrast mode supported
- Focus indicators are visible
- All interactive elements have labels

✅ **Performance**
- Page loads in under 2 seconds
- Animations run at 60fps
- No layout shifts
- Efficient file operations

✅ **Production Ready**
- Runs as systemd service
- Nginx config provided
- HTTPS instructions included
- Security best practices followed
- Comprehensive documentation

## Inspiration References

Think of this project as combining:
- **Apple's design language**: Refined, elegant, premium feel
- **Stripe's Dashboard**: Clean, functional, beautiful
- **Linear's UI**: Smooth animations, glass morphism done right
- **Vercel's Interface**: Modern, fast, delightful

The end result should feel like a **commercial product**, not a hobby project.

## Quick Reference: Key Design Elements

### The 5 Animated Blobs (CSS)
```css
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(150px);
  opacity: 0.7;
  animation: float 25s ease-in-out infinite alternate;
}

.blob-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(45deg, #6366f1, #4f46e5);
  top: -10%;
  left: -5%;
  animation-duration: 20s;
}

.blob-2 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  top: 20%;
  right: -10%;
  animation-duration: 25s;
}

/* ...blob-3, blob-4, blob-5 with different sizes, positions, colors, durations */

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(15%, 10%); }
  66% { transform: translate(-10%, 15%); }
}
```

### Glass Button Component (HTML + CSS)
```html
<button class="glass-button">
  <svg class="button-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
    <!-- Icon path here -->
  </svg>
  <span class="button-text">Upload Files</span>
  <svg class="button-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
</button>
```

```css
.glass-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glass-button:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.4), 0 0 40px rgba(6, 182, 212, 0.2);
}

.glass-button .button-arrow {
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.glass-button:hover .button-arrow {
  opacity: 1;
  transform: translateX(0);
}

.glass-button:focus {
  outline: 2px solid rgba(99, 102, 241, 0.5);
  outline-offset: 2px;
}
```

### File Card Component
```html
<div class="file-card animate-on-load">
  <div class="file-icon">📄</div>
  <div class="file-info">
    <h3 class="file-name">document.pdf</h3>
    <p class="file-meta">2.4 MB • 2 hours ago</p>
  </div>
  <div class="file-actions">
    <button class="action-button" aria-label="Download file">
      <svg><!-- Download icon --></svg>
    </button>
    <button class="action-button" aria-label="Copy link">
      <svg><!-- Copy icon --></svg>
    </button>
    <button class="action-button" aria-label="More actions">
      <svg><!-- Three dots icon --></svg>
    </button>
  </div>
</div>
```

### Parallax JavaScript (Complete Example)
```javascript
let mouseX = 0;
let mouseY = 0;
let targetX = 0;
let targetY = 0;

document.addEventListener('mousemove', (e) => {
  targetX = (e.clientX / window.innerWidth) * 2 - 1;
  targetY = (e.clientY / window.innerHeight) * 2 - 1;
});

function animateParallax() {
  // Smooth lerp
  mouseX += (targetX - mouseX) * 0.1;
  mouseY += (targetY - mouseY) * 0.1;
  
  const blobs = document.querySelectorAll('.blob');
  blobs.forEach((blob, index) => {
    const depth = (index + 1) * 5;
    const x = mouseX * depth;
    const y = mouseY * depth;
    blob.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  });
  
  requestAnimationFrame(animateParallax);
}

animateParallax();
```

This completes the comprehensive guide for building the Glassmorphic File Manager!
