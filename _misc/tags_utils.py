import re
from urllib.parse import unquote

PIXIV_SEARCH_ILLUST = "https://www.pixiv.net/ajax/search/illustrations"
PIXIV_SEARCH_ARTWORKS = "https://www.pixiv.net/ajax/search/artworks"

def download_tags(
        url, tag, sort_order, page_start, page_end, s_mode, content_type,
        ai_type, resolution, custom_resolution, ratio, period, bookmarks,
        file_location, cookies_psshid, debug, link
):
    def verify_conditions_for_cookies(
            cookies_psshid, sort_order, content_type, ai_type,
            resolution, ratio, period, bookmarks, s_mode_match
    ):
        if cookies_psshid is None:
            conditions = {
                "sort_order": sort_order == 'newest',
                "s_mode": s_mode == s_mode_match,
                "content_type": content_type == 'illust_and_ugoira',
                "ai_type": ai_type == 'display_ai',
                "resolution": resolution == 'all',
                "ratio": ratio == 'all',
                "period": period is None,
                "bookmarks": bookmarks == 'all',
            }

            if not all(conditions.values()):
                print(
                    "Either use the default settings for all arguments or "
                    "provide a value for cookies_psshid."
                )
                exit(1)

    verify_conditions_for_cookies(
        cookies_psshid, sort_order, content_type, ai_type,
        resolution, ratio, period, bookmarks, 'perfect_match'
    )

    def extract_and_decode_tag(url, message):
        """
        Extracts and decodes a tag from the given URL based on a regex pattern.

        Parameters:
            url (str): The URL to extract the tag from.

        Returns:
            str: The decoded tag if found, or None if not found.
        """
        tag_match = re.search(r'/tags/([^/]+)/', url)

        if tag_match:
            encoded_tag = tag_match.group(1)
            return unquote(encoded_tag)

        print(message)
        return None

    def initialize_page_start(url, page_start):
        if page_start is None:
            page_match = re.search(r'p=(\d+)', url)

            if page_match:
                page = page_match.group(1)
                page_start = int(page)
            else:
                page_start = 1

        return page_start

    def extract_and_initialize_parameters(
            url, tag, sort_order, s_mode, ai_type, resolution
    ):
        if tag is None:
            tag = extract_and_decode_tag(url, "Tag required.")

            sort_order_map = {
                'newest': 'date_d',
                'oldest': 'date',
                'popular_all': 'popular_d',
                'popular_male': 'popular_male_d',
                'popular_female': 'popular_female_d'
            }
            s_mode_map = {
                'perfect_match': 's_tag_full',
                'partial_match': 's_tag',
                'title_caption': 's_tc'
            }
            ai_type_map = {'display_ai': '0', 'hide_ai': '1'}
            resolution_map = {
                'all': None,
                '3000x3000+': "&wlt=3000&hlt=3000",
                '3000x3000': "&wlt=3000&hlt=3000",
                '1000x2999px': "&wlt=1000&wgt=2999&hlt=1000&hgt=2999",
                '1000-2999x1000-2999': "&wlt=1000&wgt=2999&hlt=1000&hgt=2999",
                '<999x999': "&wgt=999&hgt=999",
                '999x999': "&wgt=999&hgt=999"
            }

            sort_order = sort_order_map.get(sort_order, sort_order)
            s_mode = s_mode_map.get(s_mode, s_mode)
            ai_type = ai_type_map.get(ai_type, ai_type)
            resolution = resolution_map.get(resolution, resolution)

        return tag, sort_order, s_mode, ai_type, resolution

    def extract_resolution_from_url(url, custom_resolution):
        if custom_resolution is None:
            resolution_match = re.search(
                r'&wlt=(\d+)&wgt=(\d+)&hlt=(\d+)&hgt=(\d+)', url
            )

            if resolution_match:
                wlt, wgt, hlt, hgt = resolution_match.groups()
                resolution = f"{wlt}-{wgt}x{hlt}-{hgt}"
            else:
                resolution_match = re.search(r'&wlt=(\d+)&hlt=(\d+)', url)

                if resolution_match:
                    wlt, hlt = resolution_match.groups()
                    resolution = f"{wlt}x{hlt}"
                else:
                    resolution_match = re.search(r'&wgt=(\d+)&hgt=(\d+)', url)

                    if resolution_match:
                        wgt, hgt = resolution_match.groups()
                        resolution = f"{wgt}x{hgt}"
                    else:
                        resolution = 'all'
        else:
            resolution = custom_resolution

        return resolution

    def extract_ratio_from_url(url):
        ratio_match = re.search(r'ratio=([-0-9.]+)', url)

        if ratio_match:
            ratio_value = float(ratio_match.group(1))
            ratio_mapping = {
                0.5: "horizontal", -0.5: "vertical", 0: "square"
            }
            return ratio_mapping.get(ratio_value, "unknown")

        return 'all'

    def extract_content_type_from_url(url):
        artworks_match = re.search(r'/artworks', url)

        if artworks_match:
            content_type = 'all'
        else:
            # Look for '?type={type}' or '&type={type}' in the URL
            type_match = re.search(r'[?&]type=([^&]+)', url)
            content_type = type_match.group(1) if type_match \
                else 'illust_and_ugoira'

        return content_type

    def extract_period_from_url(url):
        period_match = re.search(
            r'scd=(\d{4}-\d{2}-\d{2})&ecd=(\d{4}-\d{2}-\d{2})', url
        )

        if period_match:
            start_date = period_match.group(1)
            end_date = period_match.group(2)
            period = f"{start_date} to {end_date}"
        else:
            period = 'all'

        return period

    def extract_bookmarks_from_url(url):
        bookmark_match = re.search(r'blt=(\d+)', url)
        bookmark_gt_match = re.search(r'bgt=(\d+)', url)

        if bookmark_match and bookmark_gt_match:
            blt_value = bookmark_match.group(1)
            bgt_value = bookmark_gt_match.group(1)
            bookmarks = f"From {blt_value} to {bgt_value}"
        elif bookmark_match:
            blt_value = bookmark_match.group(1)
            bookmarks = f"{blt_value}+"
        else:
            bookmarks = 'all'

        return bookmarks

    def extract_ai_type_from_url(url):
        ai_type_match = re.search(r'ai_type=([^&]+)', url)

        if ai_type_match:
            ai_type = ai_type_match.group(1)

            if ai_type == '1':
                ai_type = 'hide_ai'
        else:
            ai_type = 'display_ai'

        return ai_type

    def determine_s_mode(url):
        s_mode_match = re.search(r's_mode=([^&]+)', url)
        return s_mode_match.group(1) if s_mode_match else 'perfect_match'

    def determine_sort_order(url):
        sort_order_match = re.search(r'order=([^&]+)', url)
        return sort_order_match.group(1) if sort_order_match else 'date_d'

    def format_resolution(custom_resolution):
        if custom_resolution is not None:
            res_match = re.match(
                r'(\d+)x?(\d*)-(\d+)x?(\d*)', custom_resolution
            )

            if res_match:
                wlt, hlt, wgt, hgt = res_match.groups()

                if wgt and hgt:
                    resolution = f"&wlt={wlt}&wgt={wgt}&hlt={hlt}&hgt={hgt}"
                elif wlt and hlt:
                    resolution = f"&wlt={wlt}&hlt={hlt}"
                else:
                    resolution = None

                return resolution

        return None

    def format_period(period):
        if period == 'all':
            return None

        period_match = re.match(
            r'(\d{4}-\d{2}-\d{2})x(\d{4}-\d{2}-\d{2})', period
        )

        if period_match:
            start_date, end_date = period_match.groups()
            scd_ecd_str = f"&scd={start_date}&ecd={end_date}"
            return scd_ecd_str

        return None

    def get_ratio_query_string(ratio):
        ratio_map = {
            'all': None,
            'Horizontal': '&ratio=0.5',
            'Vertical': '&ratio=-0.5',
            'Square': '&ratio=0'
        }
        return ratio_map.get(ratio, ratio)

    def get_bookmarks_query_string(bookmarks):
        bookmarks_map = {
            'all': None,
            '10000+': '&blt=10000',
            '5000-9999': '&blt=5000&bgt=9999',
            '1000-4999': '&blt=1000&bgt=4999',
            '500-999': '&blt=500&bgt=999',
            '300-499': '&blt=300&bgt=499',
            '100-299': '&blt=100&bgt=299',
            '50-99': '&blt=50&bgt=99',
            '30-49': '&blt=30&bgt=49'
        }
        return bookmarks_map.get(bookmarks, bookmarks)

    def get_content_type_quey_string(content_type):
        content_type_map = {
            'illust_and_ugoira': f"{PIXIV_SEARCH_ILLUST}/{tag}?word={tag}",
            'illust': f"{PIXIV_SEARCH_ILLUST}/{tag}?word={tag}&type=illust",
            'manga': f"{PIXIV_SEARCH_ILLUST}/{tag}?word={tag}&type=manga",
            'ugoira': f"{PIXIV_SEARCH_ILLUST}/{tag}?word={tag}&type=ugoira",
            'all': f"{PIXIV_SEARCH_ARTWORKS}/{tag}?word={tag}&type=all"
        }
        return content_type_map.get(content_type, content_type)

    def build_request_url(content_type):
        params = {
            'order': sort_order,
            's_mode': s_mode,
            'ai_type': ai_type,
            'resolution': resolution,
            'ratio': ratio,
            'period': period,
            'bookmarks': bookmarks
        }

        # Collecting non-falsy parameters
        query_params = [
            f"{key}={value}" for key, value in params.items() if value
        ]

        # Joining parameters with '&' and updating request_url
        request_url = content_type

        if query_params:
            request_url += "&" + "&".join(query_params)

        return request_url

    if link == "True":
        tag = extract_and_decode_tag(url, "Tag not found in URL.")
        sort_order = determine_sort_order(url)
        page_start = initialize_page_start(url, page_start)

        if page_end is None:
            page_end = page_start

        s_mode = determine_s_mode(url)
        content_type = extract_content_type_from_url(url)
        ai_type = extract_ai_type_from_url(url)
        resolution = extract_resolution_from_url(url, custom_resolution)
        ratio = extract_ratio_from_url(url)
        period = extract_period_from_url(url)
        bookmarks = extract_bookmarks_from_url(url)

        verify_conditions_for_cookies(
            cookies_psshid, sort_order, content_type, ai_type, resolution,
            ratio, period, bookmarks, 's_tag_full'
        )

    parameters = extract_and_initialize_parameters(
        url, tag, sort_order, s_mode, ai_type, resolution
    )
    (tag, sort_order, s_mode, ai_type, resolution) = parameters

    resolution = format_resolution(custom_resolution)
    ratio = get_ratio_query_string(ratio)
    period = format_period(period)
    bookmarks = get_bookmarks_query_string(bookmarks)
    content_type = get_content_type_quey_string(content_type)

    request_url = build_request_url(content_type)

    download_page(
        request_url, cookies_psshid, file_location, page_start, page_end
    )

def main():

if __name__ == '__main__':
    main()
