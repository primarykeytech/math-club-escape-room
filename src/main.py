"""
Retro Game Boy 4-Color Math Club Escape Room
Main Game Loop & State Machine
"""
import json
import os
import sys
import time

# Ensure project root directory is in python search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame

from src.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLOR_DARKEST,
    COLOR_DARK,
    COLOR_LIGHT,
    COLOR_LIGHTEST,
    CURSOR_BLINK_RATE_MS,
    DEFAULT_TIME_LIMIT_SECONDS,
    WRONG_ANSWER_PENALTY_SECONDS
)
from src.ui import RetroUI
from src.sound import RetroSoundFX

class EscapeRoomGame:
    def __init__(self, data_path: str = "data/escape_room.json"):
        pygame.init()
        pygame.display.set_caption("MATH CLUB ESCAPE ROOM // GAME BOY DMG-01")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.ui = RetroUI()
        self.sound = RetroSoundFX()
        # Start menacing theme music on title screen
        self.sound.play_theme_music()

        # Load game data
        self.data = self._load_data(data_path)
        self.room_title = self.data.get("room_title", "THE ESCAPE ROOM")
        self.prologue_screens = self.data.get("prologue_screens", [])
        self.stages = self.data.get("stages", [])
        self.current_stage_idx = 0
        self.current_prologue_idx = 0

        # State management: "START", "PROLOGUE", "PLAYING", "STAGE_SOLVED", "VICTORY", "GAME_OVER"
        self.state = "START"

        # Timer
        self.time_limit = self.data.get("time_limit_seconds", DEFAULT_TIME_LIMIT_SECONDS)
        self.time_remaining = float(self.time_limit)
        self.timer_active = False
        self.last_tick_time = 0

        # Command input
        self.input_text = ""
        self.cursor_visible = True
        self.last_cursor_toggle = 0

        # Visual feedback / FX
        self.status_message = ""
        self.status_color = COLOR_LIGHTEST
        self.status_timer = 0
        self.screen_shake = 0
        self.flash_alpha = 0

        # Cache images
        self.images = {}
        self._load_images()

        # Hints tracking
        self.hints_revealed = 0

    def _load_data(self, path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_images(self):
        # Load prologue images
        for p in self.prologue_screens:
            img_file = p.get("image")
            if img_file:
                img_path = os.path.join("assets", "images", img_file)
                if os.path.exists(img_path) and img_file not in self.images:
                    self.images[img_file] = pygame.image.load(img_path).convert()

        # Load stage images
        for stage in self.stages:
            img_file = stage.get("image")
            if img_file:
                img_path = os.path.join("assets", "images", img_file)
                if os.path.exists(img_path) and img_file not in self.images:
                    self.images[img_file] = pygame.image.load(img_path).convert()

        # Load ending screen images
        for key in ["victory_screen", "game_over_screen"]:
            screen_cfg = self.data.get(key, {})
            img_file = screen_cfg.get("image")
            if img_file:
                img_path = os.path.join("assets", "images", img_file)
                if os.path.exists(img_path) and img_file not in self.images:
                    self.images[img_file] = pygame.image.load(img_path).convert()

    def current_stage(self) -> dict:
        if 0 <= self.current_stage_idx < len(self.stages):
            return self.stages[self.current_stage_idx]
        return {}

    def current_prologue(self) -> dict:
        if 0 <= self.current_prologue_idx < len(self.prologue_screens):
            return self.prologue_screens[self.current_prologue_idx]
        return {}

    def start_game(self):
        """Called from START screen: routes to prologue if available, else begins play."""
        self.input_text = ""
        # Stop theme music immediately on the first press of Enter to start the game
        self.sound.stop_music()
        if self.prologue_screens:
            self.state = "PROLOGUE"
            self.current_prologue_idx = 0
            self.sound.play_enter_click()
        else:
            self.start_actual_escape()

    def start_actual_escape(self):
        """Begins countdown timer and switches to Stage 1."""
        self.state = "PLAYING"
        self.timer_active = True
        self.last_tick_time = time.time()
        self.input_text = ""
        self.hints_revealed = 0
        self.status_message = "STAGE 1 INITIATED. SOLVE THE LOCK!"
        self.status_color = COLOR_LIGHTEST
        self.sound.play_enter_click()
        # Fade out menacing music as puzzle tension begins
        self.sound.fadeout_music(1200)

    def _matches_answer(self, cmd: str, accepted_answers: list) -> bool:
        import re
        cleaned_cmd = cmd.strip().lower()
        if not cleaned_cmd:
            return False

        for acc in accepted_answers:
            acc_clean = str(acc).strip().lower()
            if cleaned_cmd == acc_clean:
                return True
            # Normalize commas, semicolons, and "and" into spaces
            norm_cmd = re.sub(r'[,;:]|\band\b', ' ', cleaned_cmd)
            norm_cmd = re.sub(r'\s+', ' ', norm_cmd).strip()

            norm_acc = re.sub(r'[,;:]|\band\b', ' ', acc_clean)
            norm_acc = re.sub(r'\s+', ' ', norm_acc).strip()

            if norm_cmd == norm_acc:
                return True

            # If both have digit sequences, compare the extracted numbers
            nums_cmd = re.findall(r'\d+', cleaned_cmd)
            nums_acc = re.findall(r'\d+', acc_clean)
            if nums_cmd and nums_acc and nums_cmd == nums_acc:
                return True

            # Also compare stripped alphanumeric for full text answers
            alphanum_cmd = re.sub(r'[^a-z0-9]', '', cleaned_cmd)
            alphanum_acc = re.sub(r'[^a-z0-9]', '', acc_clean)
            if alphanum_cmd and alphanum_cmd == alphanum_acc:
                return True
        return False

    def process_command(self, cmd: str):
        cmd = cmd.strip()

        if self.state == "START":
            if cmd.lower() in ["exit", "quit"]:
                pygame.quit()
                sys.exit(0)
            self.start_game()
            return

        if self.state == "PROLOGUE":
            if cmd.lower() in ["skip", "jump", "start"]:
                self.start_actual_escape()
            elif cmd.lower() in ["back", "prev"]:
                if self.current_prologue_idx > 0:
                    self.current_prologue_idx -= 1
                    self.sound.play_enter_click()
                else:
                    self.state = "START"
            elif cmd.lower() in ["exit", "quit"]:
                self.state = "START"
            else:
                # Advance prologue slide
                if self.current_prologue_idx + 1 < len(self.prologue_screens):
                    self.current_prologue_idx += 1
                    self.sound.play_enter_click()
                else:
                    self.start_actual_escape()
            return

        if self.state == "PLAYING":
            if not cmd:
                return
            stage = self.current_stage()
            if cmd.lower() in ["quit", "exit"]:
                self.state = "START"
                self.timer_active = False
                self.sound.play_theme_music()
                return

            if cmd.lower() == "hint":
                hints = stage.get("hints", [])
                if self.hints_revealed < len(hints):
                    self.status_message = hints[self.hints_revealed]
                    self.hints_revealed += 1
                    self.status_color = COLOR_LIGHT
                    self.sound.play_enter_click()
                else:
                    self.status_message = "NO MORE HINTS AVAILABLE FOR THIS STAGE."
                    self.status_color = COLOR_DARK
                return

            # Check puzzle answer
            accepted = stage.get("accepted_answers", [])
            if self._matches_answer(cmd, accepted):
                # Correct!
                self.sound.play_success_jingle()
                self.state = "STAGE_SOLVED"
                self.status_message = stage.get("solved_text", "LOCK OPENED!")
                self.status_color = COLOR_LIGHTEST
            else:
                # Incorrect answer penalty
                penalty = stage.get("penalty_seconds", WRONG_ANSWER_PENALTY_SECONDS)
                self.time_remaining = max(0, self.time_remaining - penalty)
                self.sound.play_error_buzz()
                self.screen_shake = 12
                self.flash_alpha = 180
                self.status_message = f"INCORRECT CODE! [-{penalty} SECONDS PENALTY]"
                self.status_color = COLOR_LIGHTEST

        elif self.state == "STAGE_SOLVED":
            if cmd.lower() in ["next", "continue", "open", "go", "proceed"] or cmd == "":
                if self.current_stage_idx + 1 < len(self.stages):
                    self.current_stage_idx += 1
                    self.state = "PLAYING"
                    self.hints_revealed = 0
                    self.status_message = f"STAGE {self.current_stage_idx + 1} BEGUN."
                else:
                    self.state = "VICTORY"
                    self.timer_active = False
                    self.sound.play_victory_fanfare()

        elif self.state in ["GAME_OVER", "VICTORY"]:
            if cmd.lower() in ["start", "restart", "retry"] or cmd == "":
                self.time_remaining = float(self.time_limit)
                self.current_stage_idx = 0
                self.current_prologue_idx = 0
                self.hints_revealed = 0
                self.state = "START"
                self.sound.play_theme_music()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    submitted = self.input_text
                    self.input_text = ""
                    self.process_command(submitted)
                elif event.key == pygame.K_BACKSPACE:
                    if self.input_text:
                        self.input_text = self.input_text[:-1]
                        self.sound.play_key_click()
                elif event.key == pygame.K_ESCAPE:
                    if self.state in ["PLAYING", "PROLOGUE"]:
                        self.state = "START"
                        self.timer_active = False
                        self.sound.play_theme_music()
                    else:
                        return False
                else:
                    # Append printable unicode characters
                    if event.unicode and len(self.input_text) < 32:
                        if event.unicode.isprintable():
                            self.input_text += event.unicode
                            self.sound.play_key_click()
        return True

    def update(self):
        now = time.time()
        # Timer update
        if self.timer_active:
            dt = now - self.last_tick_time
            self.last_tick_time = now
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.timer_active = False
                self.state = "GAME_OVER"
                self.sound.play_error_buzz()
                # Play menacing theme in background while The Professor gloats
                self.sound.play_theme_music()
        else:
            self.last_tick_time = now

        # Cursor blinking
        ticks = pygame.time.get_ticks()
        if ticks - self.last_cursor_toggle > CURSOR_BLINK_RATE_MS:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = ticks

        # Decay screen shake and flash
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 15)

    def draw(self):
        # Base screen fill
        self.screen.fill(COLOR_DARKEST)

        # Calculate optional shake offset
        shake_x = 0
        shake_y = 0
        if self.screen_shake > 0:
            import random
            shake_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_y = random.randint(-self.screen_shake, self.screen_shake)

        # Drawing surface for shake offset
        draw_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        draw_surf.fill(COLOR_DARKEST)

        # 1. Top HUD Header
        self._draw_header(draw_surf)

        # 2. Central Image Viewport
        self._draw_viewport(draw_surf)

        # 3. Narrative & Puzzle Description Box
        self._draw_narrative_box(draw_surf)

        # 4. Command Line Prompt Box
        self._draw_prompt_box(draw_surf)

        # 5. Scanlines effect overlay
        self.ui.draw_scanlines(draw_surf, step=4, alpha=40)

        # Blit to main screen with shake offset
        self.screen.blit(draw_surf, (shake_x, shake_y))

        # Red flash effect for errors / penalties
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash_surf.fill(COLOR_LIGHTEST)
            flash_surf.set_alpha(self.flash_alpha)
            self.screen.blit(flash_surf, (0, 0))

        pygame.display.flip()

    def _draw_header(self, surf: pygame.Surface):
        header_rect = pygame.Rect(20, 16, WINDOW_WIDTH - 40, 46)
        self.ui.draw_gb_panel(surf, header_rect)

        # Title on left
        title_text = self.room_title
        title_surf = self.ui.font_hud.render(title_text, True, COLOR_LIGHTEST)
        surf.blit(title_surf, (header_rect.left + 14, header_rect.top + 12))

        # Timer format MM:SS
        total_sec = int(self.time_remaining)
        mins = total_sec // 60
        secs = total_sec % 60
        time_str = f"TIME: {mins:02d}:{secs:02d}"

        # Color timer brighter or alert based on state
        t_color = COLOR_LIGHTEST
        if self.state == "PLAYING" and self.time_remaining < 300:
            t_color = COLOR_LIGHT
        elif self.state == "GAME_OVER":
            t_color = COLOR_LIGHTEST

        timer_surf = self.ui.font_hud.render(time_str, True, t_color)
        t_rect = timer_surf.get_rect(right=header_rect.right - 14, centery=header_rect.centery)
        surf.blit(timer_surf, t_rect)

        # Center status indicator
        if self.state == "PROLOGUE":
            p_badge = f"BRIEFING {self.current_prologue_idx + 1}/{len(self.prologue_screens)}"
            p_surf = self.ui.font_body_bold.render(p_badge, True, COLOR_LIGHT)
            surf.blit(p_surf, p_surf.get_rect(center=header_rect.center))
        elif self.state in ["PLAYING", "STAGE_SOLVED"]:
            stage_info = f"STAGE {self.current_stage_idx + 1}/{len(self.stages)}"
            stage_surf = self.ui.font_body_bold.render(stage_info, True, COLOR_LIGHT)
            s_rect = stage_surf.get_rect(center=header_rect.center)
            surf.blit(stage_surf, s_rect)
        elif self.state == "START":
            start_badge = self.ui.font_body.render("READY TO ESCAPE?", True, COLOR_LIGHT)
            surf.blit(start_badge, start_badge.get_rect(center=header_rect.center))
        elif self.state == "VICTORY":
            v_badge = "VAULT ESCAPED // CONQUERED"
            v_surf = self.ui.font_body_bold.render(v_badge, True, COLOR_LIGHTEST)
            surf.blit(v_surf, v_surf.get_rect(center=header_rect.center))
        elif self.state == "GAME_OVER":
            g_badge = "SYSTEM LOCKOUT // DEFEAT"
            g_surf = self.ui.font_body_bold.render(g_badge, True, COLOR_LIGHT)
            surf.blit(g_surf, g_surf.get_rect(center=header_rect.center))

    def _draw_viewport(self, surf: pygame.Surface):
        """Draws the retro stage, prologue, or closing image inside a decorated Game Boy frame."""
        vp_rect = pygame.Rect(20, 72, WINDOW_WIDTH - 40, 350)
        self.ui.draw_gb_panel(surf, vp_rect)

        img = None
        if self.state == "PROLOGUE":
            p = self.current_prologue()
            img_file = p.get("image")
            img = self.images.get(img_file)
        elif self.state == "VICTORY":
            v_cfg = self.data.get("victory_screen", {})
            img_file = v_cfg.get("image", "professor_angry_gb.png")
            img = self.images.get(img_file)
        elif self.state == "GAME_OVER":
            g_cfg = self.data.get("game_over_screen", {})
            img_file = g_cfg.get("image", "professor_gloating_gb.png")
            img = self.images.get(img_file)
        else:
            stage = self.current_stage()
            img_file = stage.get("image")
            img = self.images.get(img_file)

        if img:
            # Scale image smoothly to fit viewport while maintaining aspect ratio
            img_w, img_h = img.get_size()
            target_w = vp_rect.width - 24
            target_h = vp_rect.height - 24

            scale_ratio = min(target_w / img_w, target_h / img_h)
            new_w = int(img_w * scale_ratio)
            new_h = int(img_h * scale_ratio)

            scaled_img = pygame.transform.scale(img, (new_w, new_h))
            img_rect = scaled_img.get_rect(center=vp_rect.center)

            # Draw dark inset matte around image
            matte_rect = img_rect.inflate(8, 8)
            pygame.draw.rect(surf, COLOR_DARK, matte_rect, width=1)
            surf.blit(scaled_img, img_rect)
        else:
            # Placeholder text if image not loaded
            ph = self.ui.font_body.render("[ NO VISUAL SIGNAL ]", True, COLOR_LIGHT)
            surf.blit(ph, ph.get_rect(center=vp_rect.center))

    def _format_narrative_text(self, text: str) -> str:
        """Dynamically substitutes placeholders like {time_limit_minutes} and {penalty_seconds}."""
        if not text:
            return ""
        time_mins = int(self.time_limit // 60)
        formatted = text.replace("{time_limit_minutes}", str(time_mins))
        formatted = formatted.replace("60 minutes", f"{time_mins} minutes")
        formatted = formatted.replace("{penalty_seconds}", str(WRONG_ANSWER_PENALTY_SECONDS))
        return formatted

    def _draw_narrative_box(self, surf: pygame.Surface):
        """Draws room narrative, challenge, and status in the middle-lower box."""
        box_rect = pygame.Rect(20, 432, WINDOW_WIDTH - 40, 200)
        self.ui.draw_gb_panel(surf, box_rect)

        inner_rect = box_rect.inflate(-28, -20)
        curr_y = inner_rect.top

        if self.state == "START":
            # Start screen briefing
            t_head = self.ui.font_body_bold.render("MISSION BRIEFING // ARCHIVAL ARCHIVES", True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 28

            intro_text = self._format_narrative_text(self.data.get("intro_text", ""))
            narrative_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, inner_rect.height - 40)
            self.ui.draw_text_wrapped(surf, intro_text, narrative_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=4)

        elif self.state == "PROLOGUE":
            p = self.current_prologue()
            speaker = p.get("speaker", "THE PROFESSOR")
            title = p.get("title", "TRANSMISSION")
            t_head = self.ui.font_body_bold.render(f">> {speaker} // {title} <<", True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 26

            p_text = self._format_narrative_text(p.get("text", ""))
            narrative_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, inner_rect.bottom - curr_y)
            self.ui.draw_text_wrapped(surf, p_text, narrative_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=2)

        elif self.state == "PLAYING":
            stage = self.current_stage()
            title_txt = f"{stage.get('title', 'STAGE')} // COMBINATION LOCK"
            t_head = self.ui.font_body_bold.render(title_txt, True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 26

            # Flavor text
            flavor = stage.get("flavor_text", "")
            flavor_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, 65)
            used_h = self.ui.draw_text_wrapped(surf, flavor, flavor_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=2)
            curr_y += used_h + 8

            # Puzzle prompt (highlighted)
            puzzle = stage.get("puzzle_text", "")
            avail_puzzle_h = max(40, (inner_rect.bottom - 22) - curr_y)
            puzzle_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, avail_puzzle_h)
            used_h = self.ui.draw_text_wrapped(surf, puzzle, puzzle_rect, self.ui.font_body_bold, color=COLOR_LIGHTEST, line_spacing=2)
            curr_y += used_h + 6

            # Status message or hint feedback docked cleanly
            if self.status_message:
                status_y = min(curr_y, inner_rect.bottom - 18)
                status_surf = self.ui.font_small.render(f">> {self.status_message}", True, self.status_color)
                surf.blit(status_surf, (inner_rect.left, status_y))

        elif self.state == "STAGE_SOLVED":
            t_head = self.ui.font_body_bold.render(">> COMBINATION ACCEPTED - LOCK DISENGAGED <<", True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 32

            stage = self.current_stage()
            solved_txt = stage.get("solved_text", "The mechanism unlocks!")
            txt_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, 80)
            self.ui.draw_text_wrapped(surf, solved_txt, txt_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=4)

        elif self.state == "GAME_OVER":
            g_cfg = self.data.get("game_over_screen", {})
            speaker = g_cfg.get("speaker", "THE PROFESSOR")
            title = g_cfg.get("title", "GLOATING TRIUMPH")
            t_head = self.ui.font_body_bold.render(f">> {speaker} // {title} <<", True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 24

            dialogue = g_cfg.get("dialogue", "BWAHAHAHA! The countdown reaches zero! You lacked the talent to defeat my challenges!")
            dialogue_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, 108)
            used_h = self.ui.draw_text_wrapped(surf, dialogue, dialogue_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=2)
            curr_y += used_h + 8

            stats_y = min(curr_y, inner_rect.bottom - 18)
            stats_txt = f">> STAGES CLEARED: {self.current_stage_idx}/{len(self.stages)} | VAULT PERMANENTLY SEALED"
            stats_surf = self.ui.font_small.render(stats_txt, True, COLOR_LIGHTEST)
            surf.blit(stats_surf, (inner_rect.left, stats_y))

        elif self.state == "VICTORY":
            v_cfg = self.data.get("victory_screen", {})
            speaker = v_cfg.get("speaker", "THE PROFESSOR")
            title = v_cfg.get("title", "ENRAGED RETRIBUTION")
            t_head = self.ui.font_body_bold.render(f">> {speaker} // {title} <<", True, COLOR_LIGHTEST)
            surf.blit(t_head, (inner_rect.left, curr_y))
            curr_y += 24

            dialogue = v_cfg.get("dialogue", "WHAT?! IMPOSSIBLE! You breached my vault?! I will return with an even more devious challenge!")
            dialogue_rect = pygame.Rect(inner_rect.left, curr_y, inner_rect.width, 108)
            used_h = self.ui.draw_text_wrapped(surf, dialogue, dialogue_rect, self.ui.font_body, color=COLOR_LIGHT, line_spacing=2)
            curr_y += used_h + 8

            total_elapsed = int(self.time_limit - self.time_remaining)
            mins = total_elapsed // 60
            secs = total_elapsed % 60
            stats_y = min(curr_y, inner_rect.bottom - 18)
            stats_txt = f">> ESCAPE TIME: {mins:02d}:{secs:02d} | ALL {len(self.stages)} VAULT CHALLENGES CONQUERED!"
            stats_surf = self.ui.font_small.render(stats_txt, True, COLOR_LIGHTEST)
            surf.blit(stats_surf, (inner_rect.left, stats_y))

    def _draw_prompt_box(self, surf: pygame.Surface):
        """Draws the bottom terminal-style input bar."""
        prompt_rect = pygame.Rect(20, 642, WINDOW_WIDTH - 40, 80)
        self.ui.draw_gb_panel(surf, prompt_rect)

        # Label above input or shortcuts
        if self.state == "START":
            hint_txt = "COMMAND: PRESS [ENTER] OR TYPE 'START' TO BEGIN | TYPE 'QUIT' TO EXIT"
            prompt_label = "> "
        elif self.state == "PROLOGUE":
            is_last = (self.current_prologue_idx + 1 >= len(self.prologue_screens))
            if is_last:
                hint_txt = "PRESS [ENTER] TO ENTER THE VAULT | TYPE 'SKIP' TO BEGIN"
            else:
                hint_txt = "PRESS [ENTER] OR TYPE 'NEXT' TO CONTINUE | TYPE 'SKIP' TO BYPASS"
            prompt_label = "> "
        elif self.state == "PLAYING":
            hint_txt = "COMMANDS: ENTER ANSWER CODE | TYPE 'HINT' FOR CLUE | TYPE 'QUIT' TO RESET"
            prompt_label = "ENTER CODE > "
        elif self.state == "STAGE_SOLVED":
            hint_txt = "STAGE CLEARED! PRESS [ENTER] TO ADVANCE TO NEXT CHALLENGE"
            prompt_label = "> "
        elif self.state == "VICTORY":
            hint_txt = "VAULT CONQUERED! PRESS [ENTER] OR TYPE 'START' TO PLAY AGAIN"
            prompt_label = "> "
        elif self.state == "GAME_OVER":
            hint_txt = "VAULT SEALED! PRESS [ENTER] OR TYPE 'START' TO RETRY"
            prompt_label = "> "
        else:
            hint_txt = "PRESS [ENTER] TO RESTART"
            prompt_label = "> "

        sub_surf = self.ui.font_small.render(hint_txt, True, COLOR_DARK)
        surf.blit(sub_surf, (prompt_rect.left + 16, prompt_rect.top + 10))

        # Draw the command line text with cursor
        full_line = prompt_label + self.input_text
        text_surf = self.ui.font_hud.render(full_line, True, COLOR_LIGHTEST)
        surf.blit(text_surf, (prompt_rect.left + 16, prompt_rect.top + 34))

        if self.cursor_visible:
            cursor_x = prompt_rect.left + 16 + text_surf.get_width() + 2
            cursor_y = prompt_rect.top + 36
            cursor_rect = pygame.Rect(cursor_x, cursor_y, 10, 20)
            pygame.draw.rect(surf, COLOR_LIGHTEST, cursor_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

def main():
    game = EscapeRoomGame()
    game.run()

if __name__ == "__main__":
    main()
