import aiohttp


class AnimeNotFoundError(Exception):
    pass


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
             season,
             seasonYear,
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
                     romaji
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
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise AnimeNotFoundError

    async def from_anime_id(self, key: int):
        query = '''
         query($id: Int) {
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
                 season,
                 seasonYear,
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

        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise AnimeNotFoundError

    async def from_character_name(self, name: str):
        pass

    async def cover_from_anime_id(self, key: int):
        query = '''
         query($id: Int) {
             Media(id: $id, type: ANIME, sort: SEARCH_MATCH){
                 coverImage {
                   large
                   medium
                 },
             }
         }
        '''
        variables = {
            'id': key
        }

        response = await self.session.post(self.BASE_URL, json={'query': query, 'variables': variables})

        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise AnimeNotFoundError

    async def cover_from_anime_title(self, title: str):
        query = '''
         query($search: String) {
             Media(search: $search, type: ANIME, sort: SEARCH_MATCH){
                 coverImage {
                   large
                   medium
                 },
             }
         }
        '''
        variables = {
            'id': title
        }

        response = await self.session.post(self.BASE_URL, json={'query': query, 'variables': variables})

        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise AnimeNotFoundError

    def __del__(self):
        self.session.close()
        del self.session
