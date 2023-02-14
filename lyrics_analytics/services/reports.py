# @staticmethod
#     def _lyrics_stat_summary(lyrics):
#         lyrics = lyrics.split(" ")
#         count = len(lyrics)
#         unique_count = len(set(lyrics))
#         return {
#             "count": count,
#             "unique_count": unique_count,
#             "unique_score": unique_count / count
#         }
#
#     @staticmethod
#     def _parse_date_components(date_components: dict) -> date:
#         year = date_components.get("year") or 1
#         month = date_components.get("month") or 1
#         day = date_components.get("day") or 1
#         return date(year, month, day)
#
#     def _get_song_data(self, song_response: dict) -> dict:
#         song = self._get_song(song_response["id"])["song"]
#         lyrics = ScraperService.get_lyrics(song_response["url"])
#         stat_summary = self._lyrics_stat_summary(lyrics)
#         album_data = song.get("album")
#         if album_data is None:
#             album = None
#         else:
#             album = album_data.get("name")
#
#         date_components = song_response.get("release_date_components")
#         if type(date_components) is not dict:
#             date_components = {}
#
#         data = {
#             "name": song_response["primary_artist"]["name"],
#             "title": song_response["title"],
#             "album": album,
#             "date": self._parse_date_components(date_components)
#         }
#
#         return {**data, **stat_summary}