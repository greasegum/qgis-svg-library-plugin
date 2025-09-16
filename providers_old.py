"""
Specific implementations of SVG icon providers
"""

import json
import os
from typing import List, Optional
from urllib.parse import urlencode, quote
import zipfile
import tempfile

from .icon_providers import IconProvider, SvgIcon, SearchResult


class NounProjectProvider(IconProvider):
    """Provider for The Noun Project icons"""
    
    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        super().__init__("The Noun Project", "https://api.thenounproject.com", api_key)
        self.secret = secret
        
    def is_available(self) -> bool:
        """Check if The Noun Project provider is properly configured"""
        if not self.api_key or not self.secret:
            return False
        # For demo purposes, assume it's available if keys are provided
        return True
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search The Noun Project API"""
        if not self.api_key or not self.secret:
            # Return empty results if no API key
            return SearchResult([], 0, page, 0, False, False)
            
        # For demo purposes, return some sample icons
        # In a real implementation, you would use OAuth 1.0a authentication
        sample_icons = [
            f"{query}_icon_1", f"{query}_icon_2", f"{query}_symbol"
        ]
        
        # Filter based on page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = sample_icons[start_idx:end_idx]
        
        icons = []
        for idx, icon_name in enumerate(page_icons):
            icon = SvgIcon(
                id=f"noun_{icon_name}_{idx}",
                name=icon_name.replace('_', ' ').title(),
                url=f"https://thenounproject.com/icon/{icon_name}",
                preview_url=f"https://static.thenounproject.com/png/{icon_name}-{idx}.png",
                tags=[query, icon_name],
                license="Creative Commons Attribution 3.0",
                attribution=f"Icon by The Noun Project",
                provider=self.name,
                download_url=f"https://api.thenounproject.com/icon/{icon_name}/svg"
            )
            icons.append(icon)
        
        total_count = len(sample_icons)
        total_pages = (total_count + per_page - 1) // per_page
        
        return SearchResult(
            icons=icons,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific icon"""
        # Implementation would fetch detailed icon info
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from The Noun Project (demo implementation)"""
        try:
            # For demo purposes, create a simple SVG based on the icon name
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- {icon.name} icon from {icon.provider} -->
    <circle cx="12" cy="12" r="10" stroke="#333" stroke-width="2" fill="none"/>
    <text x="12" y="16" text-anchor="middle" font-family="Arial" font-size="10" fill="#333">
        {icon.name[:3].upper()}
    </text>
    <!-- License: {icon.license} -->
    <!-- Attribution: {icon.attribution} -->
</svg>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error creating demo SVG: {e}")
            return False


class MaterialSymbolsProvider(IconProvider):
    """Provider for Material Design Symbols"""
    
    def __init__(self):
        super().__init__("Material Symbols", "https://fonts.googleapis.com/css2")
        # Material Symbols are available via Google Fonts
        self.github_base = "https://raw.githubusercontent.com/google/material-design-icons/master"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Material Symbols (using local index or GitHub API)"""
        # Expanded list of Material Design icons for better search results

        common_icons = [
            # Navigation
            "home", "house", "arrow_back", "arrow_forward", "arrow_upward", "arrow_downward",
            "chevron_left", "chevron_right", "expand_more", "expand_less", "menu", "close",
            "apps", "more_vert", "more_horiz", "refresh", "fullscreen", "fullscreen_exit",

            # Actions
            "search", "add", "remove", "add_circle", "remove_circle", "edit", "delete",
            "save", "done", "check", "check_circle", "clear", "cancel", "undo", "redo",
            "restore", "backup", "update", "upgrade", "sync", "cached", "autorenew",

            # Communication
            "email", "mail", "message", "chat", "forum", "contact_mail", "contacts",
            "dialer_sip", "phone", "call", "voicemail", "notifications", "notifications_active",

            # Content
            "copy", "content_copy", "content_cut", "content_paste", "create", "drafts",
            "filter_list", "flag", "font_download", "forward", "gesture", "inbox",
            "link", "link_off", "mail", "markunread", "move_to_inbox", "reply", "send",

            # Device
            "computer", "desktop_mac", "desktop_windows", "developer_board", "device_hub",
            "devices", "dock", "gamepad", "headset", "keyboard", "keyboard_voice",
            "laptop", "laptop_chromebook", "laptop_mac", "laptop_windows", "memory",
            "mouse", "phone_android", "phone_iphone", "phonelink", "router", "scanner",
            "security", "sim_card", "smartphone", "speaker", "tablet", "tablet_android",
            "tablet_mac", "toys", "tv", "watch",

            # Editor
            "attach_file", "attach_money", "border_all", "border_bottom", "border_clear",
            "border_color", "border_horizontal", "border_inner", "border_left", "border_outer",
            "border_right", "border_style", "border_top", "border_vertical", "format_align_center",
            "format_align_justify", "format_align_left", "format_align_right", "format_bold",
            "format_clear", "format_color_fill", "format_color_reset", "format_color_text",
            "format_indent_decrease", "format_indent_increase", "format_italic", "format_line_spacing",
            "format_list_bulleted", "format_list_numbered", "format_paint", "format_quote",
            "format_size", "format_strikethrough", "format_textdirection_l_to_r",
            "format_textdirection_r_to_l", "format_underlined", "functions", "insert_chart",
            "insert_comment", "insert_drive_file", "insert_emoticon", "insert_invitation",
            "insert_link", "insert_photo", "merge_type", "mode_comment", "mode_edit",
            "publish", "space_bar", "strikethrough_s", "text_fields", "vertical_align_bottom",
            "vertical_align_center", "vertical_align_top", "wrap_text",

            # File
            "attachment", "cloud", "cloud_circle", "cloud_done", "cloud_download",
            "cloud_off", "cloud_queue", "cloud_upload", "file_download", "file_upload",
            "folder", "folder_open", "folder_shared", "create_new_folder",

            # Hardware
            "cast", "cast_connected", "desktop_mac", "desktop_windows", "developer_board",
            "device_hub", "devices_other", "dock", "gamepad", "headset", "keyboard",
            "keyboard_arrow_down", "keyboard_arrow_left", "keyboard_arrow_right",
            "keyboard_arrow_up", "keyboard_backspace", "keyboard_capslock", "keyboard_hide",
            "keyboard_return", "keyboard_tab", "keyboard_voice", "laptop", "laptop_chromebook",
            "laptop_mac", "laptop_windows", "memory", "mouse", "phone_android", "phone_iphone",
            "phonelink", "phonelink_off", "power_input", "router", "scanner", "security",
            "sim_card", "smartphone", "speaker", "tablet", "tablet_android", "tablet_mac",
            "toys", "tv", "watch",

            # Image
            "add_a_photo", "add_to_photos", "adjust", "assistant", "assistant_photo",
            "audiotrack", "blur_circular", "blur_linear", "blur_off", "blur_on",
            "brightness_1", "brightness_2", "brightness_3", "brightness_4", "brightness_5",
            "brightness_6", "brightness_7", "broken_image", "brush", "camera", "camera_alt",
            "camera_front", "camera_rear", "camera_roll", "center_focus_strong",
            "center_focus_weak", "collections", "color_lens", "colorize", "compare",
            "control_point", "control_point_duplicate", "crop", "crop_16_9", "crop_3_2",
            "crop_5_4", "crop_7_5", "crop_din", "crop_free", "crop_landscape", "crop_original",
            "crop_portrait", "crop_square", "dehaze", "details", "edit", "exposure",
            "exposure_neg_1", "exposure_plus_1", "exposure_zero", "filter", "filter_1",
            "filter_2", "filter_3", "filter_4", "filter_5", "filter_6", "filter_7",
            "filter_8", "filter_9", "filter_9_plus", "filter_b_and_w", "filter_center_focus",
            "filter_drama", "filter_frames", "filter_hdr", "filter_none", "filter_tilt_shift",
            "filter_vintage", "flare", "flash_auto", "flash_off", "flash_on", "flip",
            "gradient", "grain", "grid_off", "grid_on", "hdr_off", "hdr_on", "hdr_strong",
            "hdr_weak", "healing", "image", "image_aspect_ratio", "iso", "landscape",
            "leak_add", "leak_remove", "lens", "looks", "looks_3", "looks_4", "looks_5",
            "looks_6", "looks_one", "looks_two", "loupe", "monochrome_photos", "movie_creation",
            "movie_filter", "music_note", "nature", "nature_people", "navigate_before",
            "navigate_next", "palette", "panorama", "panorama_fish_eye", "panorama_horizontal",
            "panorama_vertical", "panorama_wide_angle", "photo", "photo_album", "photo_camera",
            "photo_library", "photo_size_select_actual", "photo_size_select_large",
            "photo_size_select_small", "picture_as_pdf", "portrait", "remove_red_eye",
            "rotate_90_degrees_ccw", "rotate_left", "rotate_right", "slideshow", "straighten",
            "style", "switch_camera", "switch_video", "tag_faces", "texture", "timelapse",
            "timer", "timer_10", "timer_3", "timer_off", "tonality", "transform", "tune",
            "view_comfy", "view_compact", "vignette", "wb_auto", "wb_cloudy", "wb_incandescent",
            "wb_sunny",

            # Maps
            "beenhere", "directions", "directions_bike", "directions_boat", "directions_bus",
            "directions_car", "directions_railway", "directions_run", "directions_subway",
            "directions_transit", "directions_walk", "flight", "hotel", "layers", "layers_clear",
            "local_activity", "local_airport", "local_atm", "local_bar", "local_cafe",
            "local_car_wash", "local_convenience_store", "local_dining", "local_drink",
            "local_florist", "local_gas_station", "local_grocery_store", "local_hospital",
            "local_hotel", "local_laundry_service", "local_library", "local_mall", "local_movies",
            "local_offer", "local_parking", "local_pharmacy", "local_phone", "local_pizza",
            "local_play", "local_police", "local_post_office", "local_printshop", "local_see",
            "local_shipping", "local_taxi", "map", "navigation", "person_pin", "pin_drop",
            "place", "rate_review", "restaurant_menu", "satellite", "store_mall_directory",
            "terrain", "traffic",

            # Navigation Icons
            "apps", "arrow_back", "arrow_drop_down", "arrow_drop_up", "arrow_forward",
            "cancel", "check", "chevron_left", "chevron_right", "close", "expand_less",
            "expand_more", "fullscreen", "fullscreen_exit", "menu", "more_horiz", "more_vert",
            "refresh",

            # Notification
            "adb", "airline_seat_flat", "airline_seat_flat_angled", "airline_seat_individual_suite",
            "airline_seat_legroom_extra", "airline_seat_legroom_normal", "airline_seat_legroom_reduced",
            "airline_seat_recline_extra", "airline_seat_recline_normal", "bluetooth_audio",
            "confirmation_number", "disc_full", "do_not_disturb", "do_not_disturb_alt",
            "drive_eta", "event_available", "event_busy", "event_note", "folder_special",
            "live_tv", "mms", "more", "network_locked", "no_encryption", "ondemand_video",
            "personal_video", "phone_bluetooth_speaker", "phone_forwarded", "phone_in_talk",
            "phone_locked", "phone_missed", "phone_paused", "power", "priority_high",
            "sd_card", "sms", "sms_failed", "sync", "sync_disabled", "sync_problem",
            "system_update", "tap_and_play", "time_to_leave", "vibration", "voice_chat",
            "vpn_lock", "wifi",

            # Places
            "airport_shuttle", "all_inclusive", "beach_access", "business_center", "casino",
            "child_care", "child_friendly", "fitness_center", "free_breakfast", "golf_course",
            "gym", "hot_tub", "kitchen", "pool", "room_service", "smoke_free", "smoking_rooms",
            "spa",

            # Social
            "cake", "domain", "group", "group_add", "location_city", "mood", "mood_bad",
            "notifications", "notifications_active", "notifications_none", "notifications_off",
            "notifications_paused", "pages", "party_mode", "people", "people_outline",
            "person", "person_add", "person_outline", "person_pin", "plus_one", "poll",
            "public", "school", "share", "whatshot",

            # Education (additional school-related)
            "school", "backpack", "calculate", "science", "menu_book", "auto_stories",
            "library_books", "local_library", "cast_for_education", "school_outline",

            # Toggle
            "check_box", "check_box_outline_blank", "indeterminate_check_box", "radio_button_checked",
            "radio_button_unchecked", "star", "star_border", "star_half"
        ]

        # If query is empty, return all icons
        if not query:
            matching_icons = common_icons
        else:
            # Case-insensitive search - match if query is in icon name
            query_lower = query.lower()
            matching_icons = [icon for icon in common_icons if query_lower in icon.lower()]
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('_', ' ').title(),
                url=f"https://fonts.google.com/icons?selected=Material+Icons:{icon_name}",
                preview_url=f"https://fonts.gstatic.com/s/i/materialicons/{icon_name}/v1/24px.svg",
                tags=[icon_name],
                license="Apache License 2.0",
                attribution="Material Symbols by Google",
                provider=self.name,
                download_url=f"https://fonts.gstatic.com/s/i/materialicons/{icon_name}/v1/24px.svg"
            )
            icons.append(icon)
        
        total_count = len(matching_icons)
        total_pages = (total_count + per_page - 1) // per_page
        
        return SearchResult(
            icons=icons,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        """Get details for a specific Material icon"""
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Material Symbol SVG (demo implementation)"""
        try:
            # Create a Material Design style SVG
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- {icon.name} icon from Material Symbols -->
    <rect x="2" y="2" width="20" height="20" rx="2" stroke="#1976d2" stroke-width="2" fill="none"/>
    <circle cx="12" cy="12" r="6" fill="#1976d2" opacity="0.1"/>
    <text x="12" y="16" text-anchor="middle" font-family="Roboto, Arial" font-size="8" fill="#1976d2">
        {icon.name[:4].upper()}
    </text>
    <!-- License: {icon.license} -->
</svg>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error creating Material Symbol SVG: {e}")
            return False


class MakiProvider(IconProvider):
    """Provider for Maki icons (Mapbox)"""
    
    def __init__(self):
        super().__init__("Maki", "https://github.com/mapbox/maki")
        self.raw_base = "https://raw.githubusercontent.com/mapbox/maki/main"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Maki icons"""
        # Expanded list of Maki icons for better search results
        maki_icons = [
            # Transportation
            "airport", "airfield", "heliport", "rocket", "car", "car-rental", "car-repair",
            "bus", "entrance", "ferry", "harbor", "marina", "pier", "port", "fuel", "parking",
            "parking-garage", "rail", "rail-light", "rail-metro", "subway-entrance", "train",
            "bicycle", "bicycle-share", "scooter",

            # Landmarks & Buildings
            "art-gallery", "attraction", "bank", "bar", "beer", "cafe", "casino", "castle",
            "cinema", "circle", "circle-stroked", "city", "clothing-store", "college",
            "commercial", "building", "building-alt1", "convenience", "courthouse", "dam",
            "dentist", "doctor", "embassy", "entrance-alt1", "farm", "fast-food", "fence",
            "fire-station", "florist", "fuel", "furniture", "garden", "garden-center", "gift",
            "golf", "grocery", "hairdresser", "hardware", "home", "horse-riding", "hospital",
            "hotel", "ice-cream", "industry", "information", "jewelry-store", "landmark",
            "laundry", "library", "lighthouse", "lodging", "logging", "marker", "mobile-phone",
            "monument", "mountain", "museum", "music", "natural", "optician", "paint", "park",
            "park-alt1", "parking", "parking-garage", "pharmacy", "picnic-site", "pitch",
            "place-of-worship", "playground", "police", "post", "prison", "ranger-station",
            "recycling", "religious-buddhist", "religious-christian", "religious-hindu",
            "religious-islamic", "religious-jewish", "religious-shinto", "residential-community",
            "restaurant", "restaurant-bbq", "restaurant-noodle", "restaurant-pizza",
            "restaurant-seafood", "roadblock", "school", "shelter", "shoe", "shop", "skate-park",
            "skiing", "slaughterhouse", "snowmobile", "soccer", "square", "square-stroked",
            "stadium", "star", "star-stroked", "suitcase", "sushi", "swimming", "teahouse",
            "telephone", "tennis", "theatre", "toilet", "town", "town-hall", "toy", "traffic-light",
            "triangle", "triangle-stroked", "veterinary", "viewpoint", "village", "volcano",
            "warehouse", "waste-basket", "watch", "water", "waterfall", "watermill", "wetland",
            "wheelchair", "windmill", "zoo",

            # Activities
            "amusement-park", "aquarium", "basketball", "beach", "campsite", "dog-park",
            "fishing", "fitness-centre", "gaming", "globe", "golf", "gym", "hiking", "karaoke",
            "park", "picnic-site", "playground", "skateboard", "skiing", "snowboard", "soccer",
            "sports", "stadium", "swimming", "tennis", "volleyball",

            # Services
            "american-football", "baseball", "basketball", "cricket", "football", "golf",
            "skiing", "swimming", "tennis", "volleyball",

            # Nature & Geography
            "beach", "bridge", "campsite", "cemetery", "cliff", "coast", "desert", "farm",
            "forest", "garden", "glacier", "globe", "grass", "island", "lake", "marsh",
            "meadow", "mountain", "natural", "nature-reserve", "park", "peak", "river",
            "rock", "spring", "tree", "valley", "volcano", "water", "waterfall", "wetland",
            "woods",

            # Emergency & Safety
            "danger", "defibrillator", "emergency-phone", "fire-station", "hospital", "police",
            "ranger-station", "roadblock", "shelter", "siren", "telephone", "warning",

            # Food & Drink
            "alcohol-shop", "bakery", "bar", "bbq", "beer", "cafe", "drinking-water", "fast-food",
            "ice-cream", "restaurant", "restaurant-bbq", "restaurant-noodle", "restaurant-pizza",
            "restaurant-seafood", "sushi", "teahouse", "wine",

            # Shopping
            "clothing-store", "commercial", "convenience", "florist", "furniture", "gift",
            "grocery", "hardware", "jewelry-store", "market", "mobile-phone", "optician",
            "paint", "pharmacy", "shoe", "shop", "toy",

            # Education & Culture
            "art-gallery", "college", "college-JP", "library", "monument", "museum", "music",
            "school", "school-JP", "theatre", "town-hall", "university",

            # Symbols & Markers
            "arrow", "circle", "circle-stroked", "cross", "diamond", "heart", "hexagon",
            "marker", "marker-stroked", "minus", "plus", "square", "square-stroked", "star",
            "star-stroked", "triangle", "triangle-stroked", "x"
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_icons = []
        for icon in maki_icons:
            if icon not in seen:
                seen.add(icon)
                unique_icons.append(icon)
        maki_icons = unique_icons

        # If query is empty, return all icons
        if not query:
            matching_icons = maki_icons
        else:
            # Case-insensitive search - match if query is in icon name
            query_lower = query.lower()
            matching_icons = [icon for icon in maki_icons if query_lower in icon.lower()]
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('-', ' ').title(),
                url=f"https://github.com/mapbox/maki/blob/main/icons/{icon_name}.svg",
                preview_url=f"{self.raw_base}/icons/{icon_name}.svg",
                tags=[icon_name],
                license="CC0 1.0 Universal",
                attribution="Maki Icons by Mapbox",
                provider=self.name,
                download_url=f"{self.raw_base}/icons/{icon_name}.svg"
            )
            icons.append(icon)
        
        total_count = len(matching_icons)
        total_pages = (total_count + per_page - 1) // per_page
        
        return SearchResult(
            icons=icons,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Maki SVG (demo implementation)"""
        try:
            # Create a Maki style SVG (mapping/location focused)
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- {icon.name} icon from Maki (Mapbox) -->
    <circle cx="7.5" cy="7.5" r="6" fill="#3f3f3f"/>
    <circle cx="7.5" cy="7.5" r="4" fill="white"/>
    <text x="7.5" y="10" text-anchor="middle" font-family="Arial" font-size="6" fill="#3f3f3f">
        {icon.name[:2].upper()}
    </text>
    <!-- License: {icon.license} -->
</svg>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error creating Maki SVG: {e}")
            return False


class FontAwesomeFreeProvider(IconProvider):
    """Provider for Font Awesome Free icons"""
    
    def __init__(self):
        super().__init__("Font Awesome Free", "https://github.com/FortAwesome/Font-Awesome")
        self.raw_base = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search Font Awesome Free icons"""
        # Expanded list of Font Awesome Free icons for better search results
        fa_icons = [
            # Basic UI
            "home", "house", "user", "users", "user-plus", "user-minus", "user-check",
            "user-times", "user-circle", "user-cog", "user-edit", "user-friends",
            "user-graduate", "user-lock", "user-shield", "user-tag", "user-tie",
            "search", "search-plus", "search-minus", "envelope", "envelope-open",
            "heart", "star", "star-half", "star-half-alt", "flag", "bookmark",
            "bell", "bell-slash", "comment", "comments", "thumbs-up", "thumbs-down",

            # Media
            "music", "image", "images", "film", "video", "camera", "camera-retro",
            "microphone", "microphone-alt", "microphone-slash", "volume-up",
            "volume-down", "volume-off", "volume-mute", "headphones", "podcast",
            "play", "pause", "stop", "forward", "backward", "fast-forward",
            "fast-backward", "step-forward", "step-backward", "eject",

            # Files & Folders
            "file", "file-alt", "file-archive", "file-audio", "file-code",
            "file-excel", "file-image", "file-pdf", "file-powerpoint", "file-video",
            "file-word", "file-download", "file-upload", "folder", "folder-open",
            "folder-plus", "folder-minus", "copy", "paste", "cut", "save",

            # Actions
            "download", "upload", "edit", "trash", "trash-alt", "recycle", "redo",
            "redo-alt", "undo", "undo-alt", "sync", "sync-alt", "clone", "save",
            "print", "share", "share-alt", "share-square", "reply", "reply-all",
            "forward", "expand", "compress", "external-link-alt", "external-link-square-alt",

            # Time & Calendar
            "calendar", "calendar-alt", "calendar-check", "calendar-minus",
            "calendar-plus", "calendar-times", "clock", "hourglass", "hourglass-half",
            "hourglass-start", "hourglass-end", "stopwatch", "history",

            # Maps & Navigation
            "map", "map-marked", "map-marked-alt", "map-marker", "map-marker-alt",
            "map-pin", "map-signs", "compass", "location-arrow", "route", "directions",
            "street-view", "globe", "globe-americas", "globe-europe", "globe-asia",
            "globe-africa",

            # Communication
            "phone", "phone-alt", "phone-square", "phone-square-alt", "phone-volume",
            "mobile", "mobile-alt", "tablet", "tablet-alt", "fax", "wifi",
            "bluetooth", "bluetooth-b", "signal", "broadcast-tower", "rss", "rss-square",
            "satellite", "satellite-dish", "ethernet", "network-wired",

            # Transportation
            "car", "car-alt", "car-side", "bus", "bus-alt", "bicycle", "motorcycle",
            "plane", "plane-departure", "plane-arrival", "helicopter", "rocket",
            "ship", "train", "subway", "taxi", "truck", "truck-loading", "truck-moving",
            "ambulance",

            # Shopping & Commerce
            "shopping-cart", "shopping-basket", "shopping-bag", "cart-plus",
            "cart-arrow-down", "cash-register", "credit-card", "money-bill",
            "money-bill-alt", "money-bill-wave", "money-check", "money-check-alt",
            "wallet", "coins", "piggy-bank", "dollar-sign", "euro-sign", "pound-sign",
            "rupee-sign", "yen-sign", "bitcoin", "ethereum",

            # Education & Office
            "university", "book", "book-open", "book-open-reader", "bookmark",
            "briefcase", "building", "book-atlas", "book-bookmark",
            "chart-bar", "chart-line", "chart-pie", "chart-area", "clipboard",
            "clipboard-check", "clipboard-list", "paperclip", "pen", "pen-alt",
            "pencil-alt", "pencil-ruler", "highlighter", "marker", "eraser",
            "ruler", "ruler-combined", "ruler-horizontal", "ruler-vertical",

            # Health & Medical
            "hospital", "hospital-alt", "clinic-medical", "stethoscope", "syringe",
            "pills", "prescription", "prescription-bottle", "prescription-bottle-alt",
            "thermometer", "band-aid", "first-aid", "ambulance", "heart", "heartbeat",
            "tooth", "lungs", "brain", "x-ray", "radiation", "radiation-alt",
            "biohazard", "virus", "viruses", "bacteria", "disease", "microscope",

            # Security & Privacy
            "lock", "lock-open", "unlock", "unlock-alt", "key", "shield-alt",
            "user-lock", "user-shield", "fingerprint", "id-badge", "id-card",
            "id-card-alt", "user-secret",

            # Technology
            "laptop", "laptop-code", "desktop", "server", "database", "hdd", "microchip",
            "memory", "sim-card", "keyboard", "mouse", "power-off", "plug", "ethernet",
            "usb", "code", "code-branch", "bug", "robot", "project-diagram", "sitemap",
            "terminal", "window-maximize", "window-minimize", "window-restore",
            "window-close",

            # Social Media
            "facebook", "facebook-f", "facebook-square", "twitter", "twitter-square",
            "instagram", "instagram-square", "linkedin", "linkedin-in", "github",
            "github-alt", "github-square", "gitlab", "youtube", "youtube-square",
            "pinterest", "pinterest-p", "pinterest-square", "reddit", "reddit-alien",
            "reddit-square", "whatsapp", "whatsapp-square", "telegram", "telegram-plane",
            "discord", "slack", "slack-hash", "twitch", "tiktok",

            # Weather
            "sun", "moon", "cloud", "cloud-sun", "cloud-moon", "cloud-rain",
            "cloud-showers-heavy", "cloud-sun-rain", "cloud-moon-rain", "snowflake",
            "wind", "smog", "temperature-high", "temperature-low", "thermometer-half",
            "thermometer-full", "thermometer-empty", "umbrella", "rainbow", "meteor",
            "bolt",

            # Sports & Games
            "futbol", "basketball-ball", "baseball-ball", "bowling-ball", "football-ball",
            "golf-ball", "hockey-puck", "quidditch", "table-tennis", "tennis-ball",
            "volleyball-ball", "chess", "chess-bishop", "chess-board", "chess-king",
            "chess-knight", "chess-pawn", "chess-queen", "chess-rook", "dice",
            "dice-one", "dice-two", "dice-three", "dice-four", "dice-five", "dice-six",
            "gamepad", "trophy", "medal", "award",

            # Misc Objects
            "anchor", "balance-scale", "ban", "barcode", "bars", "bed", "beer", "bell",
            "birthday-cake", "blender", "bomb", "bone", "bong", "box", "box-open",
            "boxes", "bread-slice", "brush", "bucket", "bullhorn", "bullseye", "burn",
            "calculator", "campground", "candy-cane", "cannabis", "cat", "certificate",
            "chair", "charging-station", "check", "check-circle", "check-square",
            "church", "circle", "city", "clipboard", "cloud", "cocktail", "coffee",
            "cog", "cogs", "compact-disc", "compass", "cookie", "cookie-bite", "couch",
            "crow", "crown", "cube", "cubes", "cut", "diamond", "dice", "dog", "door-closed",
            "door-open", "dot-circle", "dove", "dragon", "drum", "drum-steelpan",
            "drumstick-bite", "dumbbell", "dungeon", "egg", "ellipsis-h", "ellipsis-v",
            "exclamation", "exclamation-circle", "exclamation-triangle", "eye", "eye-slash",
            "fan", "feather", "feather-alt", "female", "fighter-jet", "fire", "fire-alt",
            "fire-extinguisher", "fish", "fist-raised", "flag", "flag-checkered", "flag-usa",
            "flask", "flushed", "frog", "frown", "frown-open", "funnel-dollar", "gas-pump",
            "gavel", "gem", "genderless", "ghost", "gift", "gifts", "glass-cheers",
            "glass-martini", "glass-martini-alt", "glass-whiskey", "glasses", "globe",
            "golf-ball", "gopuram", "grimace", "grin", "grin-alt", "grin-beam",
            "grin-beam-sweat", "grin-hearts", "grin-squint", "grin-squint-tears",
            "grin-stars", "grin-tears", "grin-tongue", "grin-tongue-squint",
            "grin-tongue-wink", "grin-wink", "grip-horizontal", "grip-lines",
            "grip-lines-vertical", "grip-vertical", "guitar", "hammer", "hamsa",
            "hand-holding", "hand-holding-heart", "hand-holding-medical", "hand-holding-usd",
            "hand-holding-water", "hand-lizard", "hand-middle-finger", "hand-paper",
            "hand-peace", "hand-point-down", "hand-point-left", "hand-point-right",
            "hand-point-up", "hand-pointer", "hand-rock", "hand-scissors", "hand-sparkles",
            "hand-spock", "hands", "hands-helping", "hands-wash", "handshake",
            "handshake-alt-slash", "handshake-slash", "hanukiah", "hard-hat", "hashtag",
            "hat-cowboy", "hat-cowboy-side", "hat-wizard", "head-side-cough",
            "head-side-cough-slash", "head-side-mask", "head-side-virus", "heading",
            "headphones", "headphones-alt", "headset", "heart", "heart-broken", "heartbeat",
            "helicopter", "highlighter", "hiking", "hippo", "history", "hockey-puck",
            "holly-berry", "home", "horse", "horse-head", "hospital", "hospital-alt",
            "hospital-symbol", "hospital-user", "hot-tub", "hotdog", "hotel", "hourglass",
            "hourglass-end", "hourglass-half", "hourglass-start", "house-damage",
            "house-user", "hryvnia", "ice-cream", "icicles", "icons", "id-badge",
            "id-card", "id-card-alt", "igloo", "image", "images", "inbox", "indent",
            "industry", "infinity", "info", "info-circle", "italic", "jedi", "joint",
            "journal-whills", "kaaba", "key", "keyboard", "khanda", "kiss", "kiss-beam",
            "kiss-wink-heart", "kiwi-bird", "landmark", "language", "laptop", "laptop-code",
            "laptop-house", "laptop-medical", "laugh", "laugh-beam", "laugh-squint",
            "laugh-wink", "layer-group", "leaf", "lemon", "less-than", "less-than-equal",
            "level-down-alt", "level-up-alt", "life-ring", "lightbulb", "link", "lira-sign",
            "list", "list-alt", "list-ol", "list-ul", "location-arrow", "lock", "lock-open",
            "long-arrow-alt-down", "long-arrow-alt-left", "long-arrow-alt-right",
            "long-arrow-alt-up", "low-vision", "luggage-cart", "lungs", "lungs-virus",
            "magic", "magnet", "mail-bulk", "male", "map", "map-marked", "map-marked-alt",
            "map-marker", "map-marker-alt", "map-pin", "map-signs", "marker", "mars",
            "mars-double", "mars-stroke", "mars-stroke-h", "mars-stroke-v", "mask",
            "medal", "medkit", "meh", "meh-blank", "meh-rolling-eyes", "memory", "menorah",
            "mercury", "meteor", "microchip", "microphone", "microphone-alt",
            "microphone-alt-slash", "microphone-slash", "microscope", "minus", "minus-circle",
            "minus-square", "mitten", "mobile", "mobile-alt", "money-bill", "money-bill-alt"
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_icons = []
        for icon in fa_icons:
            if icon not in seen:
                seen.add(icon)
                unique_icons.append(icon)
        fa_icons = unique_icons

        # If query is empty, return all icons
        if not query:
            matching_icons = fa_icons
        else:
            # Case-insensitive search - match if query is in icon name
            query_lower = query.lower()
            matching_icons = [icon for icon in fa_icons if query_lower in icon.lower()]
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_icons = matching_icons[start_idx:end_idx]
        
        icons = []
        for icon_name in page_icons:
            icon = SvgIcon(
                id=icon_name,
                name=icon_name.replace('-', ' ').title(),
                url=f"https://fontawesome.com/icons/{icon_name}",
                preview_url=f"{self.raw_base}/solid/{icon_name}.svg",
                tags=[icon_name],
                license="CC BY 4.0 License",
                attribution="Font Awesome Free by Fonticons",
                provider=self.name,
                download_url=f"{self.raw_base}/solid/{icon_name}.svg"
            )
            icons.append(icon)
        
        total_count = len(matching_icons)
        total_pages = (total_count + per_page - 1) // per_page
        
        return SearchResult(
            icons=icons,
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download Font Awesome SVG (demo implementation)"""
        try:
            # Create a Font Awesome style SVG
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- {icon.name} icon from Font Awesome Free -->
    <rect x="3" y="3" width="18" height="18" rx="3" fill="#339af0"/>
    <circle cx="12" cy="12" r="7" fill="white"/>
    <text x="12" y="15" text-anchor="middle" font-family="FontAwesome, Arial" font-size="8" fill="#339af0">
        {icon.name[:3].upper()}
    </text>
    <!-- License: {icon.license} -->
</svg>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error creating Font Awesome SVG: {e}")
            return False


class GitHubRepoProvider(IconProvider):
    """Provider for GitHub repositories containing SVG icons"""
    
    def __init__(self, repo_url: str, svg_path: str = ""):
        """
        Initialize GitHub repo provider
        
        :param repo_url: GitHub repository URL (e.g., "username/repo-name")
        :param svg_path: Path within repo where SVGs are located
        """
        super().__init__(f"GitHub: {repo_url}", "https://api.github.com")
        self.repo_url = repo_url
        self.svg_path = svg_path
        self.raw_base = f"https://raw.githubusercontent.com/{repo_url}/main"
        
    def search(self, query: str, page: int = 1, per_page: int = 20) -> SearchResult:
        """Search GitHub repository for SVG files"""
        try:
            # Use GitHub API to search for SVG files
            search_url = f"{self.base_url}/search/code"
            params = {
                'q': f'{query} extension:svg repo:{self.repo_url}',
                'page': page,
                'per_page': per_page
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                icons = []
                
                for item in data.get('items', []):
                    filename = item['name']
                    icon_name = os.path.splitext(filename)[0]
                    file_path = item['path']
                    
                    icon = SvgIcon(
                        id=file_path,
                        name=icon_name.replace('-', ' ').replace('_', ' ').title(),
                        url=item['html_url'],
                        preview_url=f"{self.raw_base}/{file_path}",
                        tags=[icon_name],
                        license="See repository license",
                        attribution=f"From {self.repo_url}",
                        provider=self.name,
                        download_url=f"{self.raw_base}/{file_path}"
                    )
                    icons.append(icon)
                
                total_count = data.get('total_count', len(icons))
                total_pages = (total_count + per_page - 1) // per_page
                
                return SearchResult(
                    icons=icons,
                    total_count=total_count,
                    current_page=page,
                    total_pages=total_pages,
                    has_next=page < total_pages,
                    has_previous=page > 1
                )
        except Exception as e:
            print(f"Error searching GitHub repo: {e}")
            
        return SearchResult([], 0, page, 0, False, False)
    
    def get_icon_details(self, icon_id: str) -> Optional[SvgIcon]:
        return None
        
    def download_svg(self, icon: SvgIcon, file_path: str) -> bool:
        """Download SVG from GitHub repository (demo implementation)"""
        try:
            # For demo, create a GitHub repo style SVG
            svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- {icon.name} icon from {self.repo_url} -->
    <rect x="1" y="1" width="22" height="22" rx="4" stroke="#24292e" stroke-width="2" fill="none"/>
    <rect x="4" y="4" width="16" height="16" rx="2" fill="#24292e" opacity="0.1"/>
    <text x="12" y="14" text-anchor="middle" font-family="monospace" font-size="7" fill="#24292e">
        {icon.name[:4].upper()}
    </text>
    <!-- From GitHub: {self.repo_url} -->
    <!-- License: {icon.license} -->
</svg>"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            return True
        except Exception as e:
            print(f"Error creating GitHub repo SVG: {e}")
            return False