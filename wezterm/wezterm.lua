local wezterm = require "wezterm";
local catppuccin = require("catppuccin").setup {
  flavour = "mocha",
};

if wezterm.target_triple == "x86_64-pc-windows-msvc" then
  default_prog = {
    "C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-nologo"
  }
  font = wezterm.font_with_fallback({
    "FiraCode NF",
    "FiraCode Nerd Font",
    "JetBrains Mono",
  })
  font_size = 13
else
  default_prog = {"/bin/zsh", "-l"}
  font = wezterm.font_with_fallback({
    "FiraCode Nerd Font",
    "JetBrains Mono",
  })
  font_size = 16
end

return {
  default_prog = default_prog,
  initial_cols = 88,
  initial_rows = 24,
  default_cursor_style = "BlinkingBlock",
  use_fancy_tab_bar = false,
  cursor_blink_rate = 600,
  enable_scroll_bar = true,

  font = font,
  font_size = font_size,
  freetype_load_target = "Light",
  freetype_render_target = "HorizontalLcd",

  colors = catppuccin,
  --[[colors = {
      -- The default text color
      foreground = "#D0CEC3",
      -- The default background color
      background = "#1F2430",

      -- Overrides the cell background color when the current cell is occupied by the
      -- cursor and the cursor style is set to Block
      cursor_bg = "#ECEADD",
      -- Overrides the text color when the current cell is occupied by the cursor
      cursor_fg = "#000000",
      -- Specifies the border color of the cursor when the cursor style is set to Block,
      -- or the color of the vertical or horizontal bar when the cursor style is set to
      -- Bar or Underline.
      cursor_border = "#41B487",

      -- the foreground color of selected text
      selection_fg = "#000000",
      -- the background color of selected text
      selection_bg = "#ECEADD",

      -- The color of the scrollbar "thumb"; the portion that represents the current viewport
      scrollbar_thumb = "#222222",

      -- The color of the split lines between panes
      split = "#333842",

      ansi = {"#111418", "#FC1827", "#75A805", "#FECD6D", "#42A4E0", "#9161C0", "#41B487", "#607387"},
      brights = {"#383C44", "#EA5965", "#ADE46B", "#FFEC88", "#4EC5E0", "#C9AEFF", "#86E2BF", "#FFFFFF"},
  },--]]

  mouse_bindings = {
    -- Change the default selection behavior so that it only selects text,
    -- but doesn't copy it to a clipboard or open hyperlinks.
    {
      event={Up={streak=1, button="Left"}},
      mods="NONE",
      action=wezterm.action{ExtendSelectionToMouseCursor="Cell"}
    },
    {
      event={Up={streak=1, button="Left"}},
      mods="SHIFT",
      action="Nop",
    },
    -- Don't automatically copy the selection to the clipboard
    -- when double clicking a word
    {
      event={Up={streak=2, button="Left"}},
      mods="NONE",
      action="Nop",
    },
    -- Ctrl-click will open the link under the mouse cursor
    {
      event={Up={streak=1, button="Left"}},
      mods="CTRL",
      action="OpenLinkAtMouseCursor",
    },
    -- Disable the 'Down' event of CTRL-Click to avoid weird program behaviors
    {
      event={Down={streak=1, button="Left"}},
      mods="CTRL",
      action="Nop",
    },
  },

  keys = {
    {
      key="c",
      mods="CTRL",
      action = wezterm.action_callback(function(win, pane)
        local has_selection = win:get_selection_text_for_pane(pane) ~= ""
        if has_selection then
          win:perform_action(wezterm.action{CopyTo="ClipboardAndPrimarySelection"}, pane)
	  window:perform_action("ClearSelection", pane)
        else
          win:perform_action(wezterm.action{SendKey={key="c", mods="CTRL"}}, pane)
        end
      end)
    }
  }
}
