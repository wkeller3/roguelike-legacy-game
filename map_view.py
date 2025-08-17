# map_view.py
import pygame
import constants as C


def draw_map(screen, game_map):
    """
    Draws a full-screen map overlay, now correctly showing all connections,
    walls, and hints for unexplored paths in all four directions.
    """
    # --- Create Overlay Surface ---
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill(C.MAP_BG)

    # --- Map Drawing Parameters ---
    room_size = 20
    room_margin = 10
    total_tile_size = room_size + room_margin

    screen_center_x = screen.get_width() / 2
    screen_center_y = screen.get_height() / 2
    player_room_coords = game_map.current_room_coords

    # --- Pass 1: Draw each explored room's square ---
    room_rects = {}
    for room_coords in game_map.explored_rooms:
        room = game_map.rooms.get(room_coords)
        if not room:
            continue
        rel_x = room_coords[0] - player_room_coords[0]
        rel_y = room_coords[1] - player_room_coords[1]
        draw_x = screen_center_x + rel_x * total_tile_size - (room_size / 2)
        draw_y = screen_center_y + rel_y * total_tile_size - (room_size / 2)
        rect = pygame.Rect(draw_x, draw_y, room_size, room_size)
        room_rects[room_coords] = rect

        # Determine color
        if room_coords == player_room_coords:
            color = C.MAP_PLAYER
        elif room.is_cleared:
            color = C.MAP_CLEARED
        else:
            color = C.MAP_EXPLORED

        pygame.draw.rect(overlay, color, rect)

    # --- Draw the explicit exit icon ---
    exit_map = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}
    if game_map.entry_direction in exit_map:
        exit_coords = exit_map[game_map.entry_direction]
        rel_x = exit_coords[0] - player_room_coords[0]
        rel_y = exit_coords[1] - player_room_coords[1]
        draw_x = screen_center_x + rel_x * total_tile_size - (room_size / 2)
        draw_y = screen_center_y + rel_y * total_tile_size - (room_size / 2)
        exit_rect = pygame.Rect(draw_x, draw_y, room_size, room_size)
        pygame.draw.rect(overlay, C.MAP_EXIT, exit_rect, border_radius=4)

    # --- Pass 2: Draw connections and hints for ALL FOUR directions ---
    for room_coords, rect in room_rects.items():
        x, y = room_coords

        # Define neighbor coordinates
        north_coords = (x, y - 1)
        south_coords = (x, y + 1)
        east_coords = (x + 1, y)
        west_coords = (x - 1, y)

        # Check NORTH
        if north_coords in room_rects:
            pygame.draw.line(
                overlay,
                C.MAP_CONNECTION,
                rect.midtop,
                room_rects[north_coords].midbottom,
                2,
            )
        elif north_coords in game_map.rooms:
            start_pos = rect.midtop
            end_pos = (start_pos[0], start_pos[1] - room_margin / 2)
            pygame.draw.line(overlay, C.MAP_UNEXPLORED_PATH, start_pos, end_pos, 2)

        # Check SOUTH
        if south_coords in room_rects:
            pygame.draw.line(
                overlay,
                C.MAP_CONNECTION,
                rect.midbottom,
                room_rects[south_coords].midtop,
                2,
            )
        elif south_coords in game_map.rooms:
            start_pos = rect.midbottom
            end_pos = (start_pos[0], start_pos[1] + room_margin / 2)
            pygame.draw.line(overlay, C.MAP_UNEXPLORED_PATH, start_pos, end_pos, 2)

        # Check EAST
        if east_coords in room_rects:
            pygame.draw.line(
                overlay,
                C.MAP_CONNECTION,
                rect.midright,
                room_rects[east_coords].midleft,
                2,
            )
        elif east_coords in game_map.rooms:
            start_pos = rect.midright
            end_pos = (start_pos[0] + room_margin / 2, start_pos[1])
            pygame.draw.line(overlay, C.MAP_UNEXPLORED_PATH, start_pos, end_pos, 2)

        # Check WEST
        if west_coords in room_rects:
            pygame.draw.line(
                overlay,
                C.MAP_CONNECTION,
                rect.midleft,
                room_rects[west_coords].midright,
                2,
            )
        elif west_coords in game_map.rooms:
            start_pos = rect.midleft
            end_pos = (start_pos[0] - room_margin / 2, start_pos[1])
            pygame.draw.line(overlay, C.MAP_UNEXPLORED_PATH, start_pos, end_pos, 2)

    # --- NEW: Pass 3: Draw the line connecting the entrance to the exit ---
    start_room_rect = room_rects.get((0, 0))
    if start_room_rect and exit_rect:
        start_pos = start_room_rect.center
        end_pos = exit_rect.center

        # Connect the correct edges for a cleaner look
        if game_map.entry_direction == "NORTH":
            start_pos = start_room_rect.midtop
            end_pos = exit_rect.midbottom
        elif game_map.entry_direction == "SOUTH":
            start_pos = start_room_rect.midbottom
            end_pos = exit_rect.midtop
        elif game_map.entry_direction == "WEST":
            start_pos = start_room_rect.midleft
            end_pos = exit_rect.midright
        elif game_map.entry_direction == "EAST":
            start_pos = start_room_rect.midright
            end_pos = exit_rect.midleft

        pygame.draw.line(overlay, C.MAP_EXIT, start_pos, end_pos, 2)

    # Blit the final overlay onto the main screen
    screen.blit(overlay, (0, 0))
