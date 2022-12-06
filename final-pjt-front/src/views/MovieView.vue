<template>
  <div>
    <div class="list-container">
      <div v-if="recommendMovies.length > 0" class="main-text">
        <h1>당신을 위한 영화</h1>
      </div>
      <div v-if="recommendMovies.length > 0" class="list-card">
        <LikeToRecommend
        v-for="(movie,index) in recommendMovies"
        :key="index"
        :movie="movie"
        />
      </div>
      <hr v-if="recommendMovies.length > 0">
    </div>
    
    <div class="list-container">
      <div v-if="followMovies.length > 0" class="main-text">
        <h1>팔로우의 선택</h1>
      </div>
      <div v-if="followMovies.length > 0" class="list-card">
        <FollowLikeMovies
        v-for="movie in followMovies"
        :key="movie.id"
        :movie="movie"
        />
      </div>
      <hr v-if="followMovies.length > 0" >
    </div>

    <div class="list-container">
      <div v-if="trendMovies.length > 0" class="main-text">
        <h1>WHAT FLIX HOT MOVIE</h1>
      </div>
      <div v-if="trendMovies.length > 0" class="list-card">
        <LikeToRecommend
        v-for="movie in trendMovies"
        :key="`s-${movie?.id}`"
        :movie="movie"
        />
      </div>
    </div>
    <hr>
    <div class="list-container">
      <div class="main-text">
        <h1>현재 상영작</h1>
      </div>
      <div class="list-card">
        <UpcomingMovie
        v-for="movie in upcomingMovies"
        :key="`a-${movie?.id}`"
        :movie="movie"
        />
      </div>
    </div>
    <hr>
      <div class="list-container">
        <div class="main-text">
          <h1>전체 영화</h1>
        </div>
        <div class="list-card">
          <MovieList
            v-for="(movie, index) in movies"
            :key="`b-${movie?.id}`"
            :movie="movie"
            :index="index"
            :limit="limit"
          />
        </div>
        </div>
        <infinite-loading id="movie" @infinite="infiniteHandler">
        </infinite-loading>  
  </div>
</template>

<script>
import MovieList from '@/components/MovieList.vue'
import UpcomingMovie from '@/components/UpcomingMovie.vue'
import LikeToRecommend from '@/components/LikeToRecommend.vue'
import InfiniteLoading from 'vue-infinite-loading'
import FollowLikeMovies from '@/components/FollowLikeMovies.vue'

export default {
  name: 'MovieView',
  components: {
    MovieList,
    UpcomingMovie,
    LikeToRecommend,
    InfiniteLoading,
    FollowLikeMovies,
  },
  data() {
    return {
      limit: 30,
      isLoading: 0,
    }
  },
  computed: {
    cnt() {
      return this.$store.state.cnt
    },
    movies() {
        return this.$store.state.movies
    },
    upcomingMovies() {
      // console.log('호잇1')
      // console.log(this.$store.state.upcomingMovies)
      return this.$store.state.upcomingMovies
    },
    recommendMovies() {
      // console.log('호잇2')
      return this.$store.state.recommendMovies
    },
    trendMovies() {
      // console.log('호잇3')
      return this.$store.state.trendMovies
    },
    followMovies() {
      // console.log('호잇4')
      return this.$store.state.followMovies
    }
  },
  created() {
    this.getMovies()
    this.getUpcomingMovie()
    this.LikeToRecommend()
    this.TrendMovies()
    this.getFollowMovies()
  },
  methods: {
    getFollowMovies() {
      this.$store.dispatch('getFollowMovies')
    },
    getMovies() {
       if (this.cnt === 0) {
         this.$store.dispatch('getMovies')
         this.$store.commit('RESET_MOVIES')
       } else {
        this.$store.commit('RESET_MOVIES')
       }
    },
    getUpcomingMovie() {
        this.$store.dispatch('getUpcomingMovie')
    },
    LikeToRecommend() {
      this.$store.dispatch('likeToRecommend')
    },
    TrendMovies() {
      this.$store.dispatch('trendMovies')
    },
    infiniteHandler($state) {
      if (this.limit < this.$store.state.movies.length) {
        setTimeout(this.limit += 30, 2000)
        $state.loaded()
      } else {
        $state.complete()
      }
    }
  },  
}
</script>

<style>
  .list-container {
    width: 1200px;
    /* display: flex; */
    
}
.list-card{
      display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.main-text {
text-align: left; 
margin-left: 68px;
}
</style>
<!--
[22/Nov/2022 23:39:00] "POST /api/v1/movies/history/851644/ HTTP/1.1" 201 0
[22/Nov/2022 23:39:00] "GET /user/ HTTP/1.1" 200 69
[22/Nov/2022 23:39:00] "GET /api/v1/movies/1/ HTTP/1.1" 200 756
[22/Nov/2022 23:39:00] "GET /api/v1/casts/851644/ HTTP/1.1" 200 2651
[22/Nov/2022 23:39:00] "GET /api/v1/movies/like/1/ HTTP/1.1" 200 15
Not Found: /community/reviews/1/
[22/Nov/2022 23:39:00] "GET /community/reviews/1/ HTTP/1.1" 404 37
[22/Nov/2022 23:39:00] "GET /api/v1/movies/poster/851644/ HTTP/1.1" 200 581
[22/Nov/2022 23:39:00] "GET /api/v1/movies/related/851644/ HTTP/1.1" 200 4192
 -->