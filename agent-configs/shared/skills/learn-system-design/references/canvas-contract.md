# Offline whiteboard presentation contract

## Board layout and visual language

Use one continuous two-dimensional board in a viewport that fills the browser window. Use three horizontal regions: functional and non-functional requirements stacked in the first column; core entities above API / system interface in the second; the evolving architecture in the large right region. Use these section names explicitly for populated sections; omit empty entity, interface, or requirement-kind sections when outside the prompt's scope. Do not stack APIs beneath the first column. For a prompt that forbids architecture diagrams, use that right-side region for the permitted schema or product-flow views. Preserve earlier context as later steps appear. For example, a deep dive can focus on the database while requirements remain reachable by panning left.

Use a white background and dark text. Generate SVG vectors with the pinned, bundled Rough.js renderer and stable seeds. Follow the [architecture diagram rules](diagram-patterns.md) for shapes, ingress, and left-to-right flow. Use visibly irregular, lightly doubled strokes for shapes and connectors, similar to an Excalidraw sketch. A barely perceptible displacement filter alone is insufficient. Check the appearance at the normal presentation zoom, not just in an enlarged preview. Keep text outside distortion filters. Use an Excalidraw-like handwritten font for all canvas text, including bullets, tables, code snippets, and diagrams; use Nunito only inside canvas Notes. Embed or bundle a legally redistributable font, such as Excalifont, with its required license. Use embedded Nunito for application controls, the Question panel, and all other non-canvas components; include its license. Never load remote fonts at runtime. Wait for the embedded font before calculating the initial camera view.

Keep labels concise and directions unambiguous. Center the primary architecture path vertically within its reserved diagram bounds, with dependencies above and below. Use separate angled straight connectors rather than orthogonal fan-out trunks. This diagram composition does not recenter the board, text sections, or camera on step changes. Preserve component positions and identities across architecture states where practical. Replace changed architecture in the same right-side region. Use focused subdiagrams when the complete architecture would become unreadable.

Apply Diagram Design's node and connector limits to focused figures, not the entire whiteboard. Avoid shadows inside figures; use interface elevation where it distinguishes controls. Give each SVG unique title/description ID prefixes and accessible naming. Do not render the whole presentation as a raster image.

Keep the fitted board within a horizontal monitor viewport, allowing varied font sizes by content role. Use compact bullet fragments in every main-board text section; reserve full sentences, tables, and long explanations for study notes or the original question. Keep assumptions and exclusions in the relevant study notes rather than extending the requirements column. Constrain diagram and note height; use scrollable notes instead of stretching the board downward. Do not shrink all text to compensate for verbose content.

## Presentation states

Store content state separately from camera position. Each step determines visible content and the architecture version. Preserve the current zoom and pan offset when changing steps, including through buttons, arrow keys, or the step selector. Set an initial readable view once; recenter only through explicit Focus step or Fit all controls. Anchor evolving content at stable board coordinates, with a fixed top edge rather than vertical centering based on content height. New bullets should extend downward without shifting existing content. Manual exploration never advances the solution.

Implement these behaviors:

- Previous/Next buttons and Left/Right arrow keys navigate steps, with disabled controls at boundaries.
- Reveal at most one section per step; group related requirements, entities, or API operations when they can be explained together. Use explicit record IDs in the reveal schedule; never reveal all functional and non-functional requirements together. Keep the board regions fixed while allowing sections to interleave across steps. Retain the latest diagram during later reveals and anchor Notes to the newly introduced record.
- Retain earlier bullets at stable coordinates. Render per-step talking points only in Notes; require an explicit explanation in Notes before removing or replacing durable diagram content. Hide future bullets with reserved layout space and remove them from interaction and the accessibility tree. Backward navigation restores earlier architecture and hides only later content.
- A visible step counter and section name identify the current position.
- Store the one-based slide number in the URL fragment, such as `#19`. Restore it on load and respond to fragment changes without moving the camera. Clamp out-of-range numbers to the nearest step; use step 1 for missing or invalid fragments. Update the fragment with replacement history when navigating, without creating a browser-history entry for each slide. Titles and step IDs must not determine the link.
- “Focus step” restores the current step's intended view after exploration.
- “Fit all” fits content revealed at the current step without revealing future answers.
- A notes visibility control hides supplementary notes without removing presentation content.

Fill the browser viewport in layout. The Full screen button must invoke the Fullscreen API only after a user action and tolerate unsupported or rejected requests. Fullscreen permission must not be necessary for use.

## Panning, zooming, and focus

Support all three panning gestures: left-button drag on blank canvas, middle-button hold-drag on blank canvas or non-interactive board content, and Space+drag. Suppress browser autoscroll for middle-button canvas gestures. Wheel gestures over the canvas zoom around the pointer, with or without Ctrl/Cmd; they do not pan. Provide canvas zoom buttons as well. Prevent native browser zoom from Ctrl/Cmd+wheel, including over application controls or panels; only canvas gestures change the canvas transform. Keep ordinary panel scrolling independent. Preserve native Ctrl/Cmd+plus and Ctrl/Cmd+minus keyboard shortcuts without intercepting them. Never implement canvas zoom by scaling the page or its controls. Clamp zoom to usable bounds and avoid camera jumps on resize.

Keep movement distinct from text selection and control interaction. Disable text selection across the interactive canvas, including HTML requirements, entity fields, APIs, and SVG labels. Let left-button dragging on non-interactive board content pan the canvas. Keep the untransformed question panel selectable. Do not start canvas dragging during text selection or operation of buttons, links, or Notes scrollers. In Notes, left-button vertical dragging scrolls the content with scale-corrected pointer deltas; disable selection there during interactive use. Preserve native wheel and scrollbar scrolling, keyboard focus, and link activation. Clear drag state on release, cancellation, capture loss, or window blur. Ignore navigation shortcuts in editable fields and with conflicting modifiers. Do not intercept ordinary arrow keys inside a scrollable study-note panel.

Provide visible keyboard focus and keyboard-operable camera controls. Keep navigation controls outside the transformed board. Overlay a floating top toolbar for Question, Notes, and Full screen. Use a compact, single-row bottom bar for step selection, zoom, Focus step, and Fit all. Put equal-width, icon-only Previous/Next buttons at the far right with accessible labels. Omit directional pan buttons; support Shift+arrow keys for keyboard panning. Provide gesture help through accessible descriptions or tooltips instead of adding another toolbar row. Explicit camera-fit controls must account for overlaid controls. Arrow navigation must not be the only way to use the presentation.

## Question reference panel

Embed the full supplied system design question as static semantic HTML in a toggleable right-side panel outside the transformed canvas. Preserve the question's wording, constraints, examples, and meaningful formatting. Include relevant supplied figures as local or embedded assets. Keep solution assumptions and study notes separate from the original question. For a brief prompt, display that prompt without inventing a longer question.

Provide a persistent “Question” toggle and a labeled close button. Start with the panel closed and make it available at every presentation step. Do not copy the complete question into a canvas node; keep the canvas's concise requirements and solution content.

Implement the panel as a non-modal, independently scrollable region:

- Extend the drawer from the viewport top to bottom, including behind the toolbar area; keep its header fixed and its body independently scrollable.
- Keep its text selectable and readable. Canvas zoom must not change the panel text size.
- Preserve the current presentation step and camera position when opening or closing it. Fit all and Focus step must account for the visible panel's occupied width.
- Keep pointer, wheel, and keyboard interactions inside the panel from panning the board or advancing steps, including at scroll boundaries.
- Expose expanded state and the controlled region through the toggle. Move focus into the panel on opening, return focus to the toggle on closing, and support Escape while focus is inside it.
- Remove the closed panel from keyboard navigation and the accessibility tree. Respect reduced motion for any slide-in transition.

Escape supplied text and sanitize any rendered markup rather than executing embedded HTML or scripts. Include the full question in no-JavaScript and print views even when the interactive panel is closed. Its content must be embedded at generation time, with no runtime fetch or external frame.

## Supplementary notes

Place the current slide's Notes block beside its newly revealed bullet, changed diagram node, or current diagram. Connect it to that target with a thin curved annotation arrow pointing toward the target, leaving a 12-unit gap before the referenced text or shape. Use 16px note text and an 18px Notes heading at native canvas scale; users can zoom for closer reading. Notes are ephemeral: replace and reposition them per step, while retaining the main content and camera. Use a subtle contrasting background, hand-drawn outlines, Nunito text, and an explicit “Notes” label. Position notes independently of main layout so showing, hiding, or moving them cannot shift the board content. Remove hidden notes from interaction and keyboard navigation, but restore them in print output. Color alone must not identify them. Keep the main board concise while notes explain particular decisions and likely interviewer follow-ups. Do not let long notes force auto-fit to shrink the main explanation below a comfortable reading size. Place notes alongside it, use independently scrollable detail, or split dense steps.

Let long notes expand or scroll without shrinking the entire canvas text. Include expanded note bounds when fitting content, or present expanded detail in an accessible untransformed panel. For example, explain a crash between database commit and message acknowledgment and the selected deduplication mechanism.

Treat notes as optional discussion depth, not prohibited interview content. Use “If asked about…” prompts where helpful. Preserve readable contrast. Notes use drag scrolling in the interactive view; retain selectable text in print and no-JavaScript output.

## Offline implementation and accessibility

Make the artifact usable through `file://` with networking disabled. Embed data instead of fetching local JSON. Avoid module imports or other features requiring an HTTP origin. Do not depend on CDN libraries, analytics, APIs, service workers, or build tools at viewing time.

Use semantic DOM text and accessible controls even when SVG draws architecture. Provide meaningful diagram descriptions and textual explanations of important flows. Keep hidden future content out of keyboard navigation and the accessibility tree. If browser storage is used, tolerate denied storage without breaking the presentation.

Respect reduced motion by changing camera and diagram state immediately. Step navigation must remain available. Prefer static diagram states over Diagram Design's animation controller; canvas state changes are application navigation.

Provide readable no-JavaScript and print fallbacks with final board content and study notes in document order. Avoid printing a clipped viewport or shrinking an entire board to illegible text. Reuse authored content where possible so fallback explanations stay consistent.

## Acceptance checks

Verify these behaviors against the generated artifact:

1. Open through `file://` with networking disabled. Confirm all content and controls work without network requests for required assets.
2. Advance through the sequence, then step backward across each architecture change. Confirm earlier states are restored without future content and that forward/backward navigation preserves a manually changed zoom and pan offset.
3. Pan in both axes using left-button and middle-button hold-drag, verify that releasing the button stops panning, and zoom around the pointer. Verify plain wheel and Ctrl/Cmd+wheel change only the canvas scale around the pointer, while the application does not intercept native browser zoom keyboard shortcuts. Use Focus step and Fit all after moving far away; confirm they recover the expected view.
4. Operate buttons, links, selectable text, and long notes. Confirm scrolling or dragging them does not accidentally move the board or change steps. Compare main-content bounds and the camera transform before and after toggling notes; both must remain unchanged.
5. Use keyboard-only controls. Confirm visible focus, readable labels, boundary behavior, and exclusion of hidden content from focus order.
6. Inspect at laptop and desktop sizes, such as 1366×768 and 1920×1080. Check the rendered text size after canvas scaling, not only its CSS font size. Aim for at least 16px main text at the focused view; split dense content or provide focused detail when necessary. Confirm controls remain usable with the Question panel open. Verify the bottom bar stays one row and the two navigation buttons have equal widths.
7. Enable reduced motion and inspect no-JavaScript and print fallbacks. Confirm the complete solution remains accessible.
8. Inspect SVG identifiers, connectors, and labels for overlaps or broken references. Check the browser console for errors.
9. Cross-check final architecture, APIs, schema, and notes against prioritized requirements.
10. Compare the question panel with the supplied prompt. Toggle it at different steps and zoom levels; verify independent scrolling, focus placement after the opening transition, focus restoration, unchanged solution state, offline access, and inclusion in print and no-JavaScript views.

Use available browser automation or manual browser tooling for runtime checks. If neither is available, perform static checks and disclose that runtime interactions remain unverified. Do not equate a syntax check with a verified offline presentation.

## Progressive entity modeling

Start with the minimum identities and fields needed to discuss the functional requirements, usually two to four fields per entity. Defer recovery identities, versions, indexes, and operational fields until a baseline operation or deep dive needs them. Keep invariants in Notes.

Use optional step `entity_update: {"id": "reservation", "fields": ["reservationId", "state", "idempotencyKey"], "reason": "Persist retry identity before retrying ambiguous writes."}` to replace one entity's field list explicitly. Include all fields that remain; explain additions, renames, and removals in `reason`, which appears in Notes. Use updates only after that entity has been revealed on an earlier step, with `reveal: null` in a baseline, deep-dive or summary step. Keep the same entity ID and board location. The renderer reserves the largest version's space, restores earlier versions on Previous, and anchors Notes to the changed entity. Print and no-JavaScript views show final fields; per-step Notes explain evolution. Do not reveal the final production schema at the start.

Use compact text sections comparable to rendered diagram labels: 14px body text, 18px section headings, and 13px entity fields at native canvas scale. Reserve the largest entity version before placing APIs below it; changing a model must not move the API section or camera.
