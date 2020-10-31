import aiohttp
import json


class AnimeList:
    BASE_URL = 'https://graphql.anilist.co'

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def from_anime_name(self, name: str):
        query = '''
        query($search: String) {
         Media(search: $search, type: ANIME, sort: SEARCH_MATCH){
             title {
               romaji
             },
             coverImage {
               large
               medium
             },
             episodes,
             genres,
             duration,
             status,
             averageScore,
             source,
             studios {
               edges {
                 node{
                   name,
                   isAnimationStudio,
                 }
               }
             },
             relations {
               edges {
                 relationType,
                 node {
                   title {
                     english
                   } 
                 }
               }
             },
         }
        }
        '''
        variables = {
         'search': name
        }

        response = await self.session.post(self.BASE_URL, json={'query': query, 'variables': variables})

        return await response.json()

    async def from_anime_id(self, key: str):
        query = '''
         query($id: String) {
             Media(id: $id, type: ANIME, sort: SEARCH_MATCH){
                 title {
                   romaji
                 },
                 coverImage {
                   large
                   medium
                 },
                 episodes,
                 genres,
                 duration,
                 status,
                 averageScore,
                 source,
                 studios {
                   edges {
                     node{
                       name,
                       isAnimationStudio,
                     }
                   }
                 },
                 relations {
                   edges {
                     relationType,
                     node {
                       title {
                         english
                       }
                     }
                   }
                 },
             }
         }
        '''
        variables = {
            'id': key
        }

        response = await self.session.post(self.BASE_URL, json={'query': query, 'variables': variables})

        return await response.json()

    async def from_character_name(self, name: str):
        pass

    def __del__(self):
        self.session.close()
        del self.session
        del self.BASE_URL
