import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import searchResult from '../components/searchResult.vue'
import Paper from '../components/paper.vue'
import SignUp from '../components/signup.vue'
import LogIn from '../components/login.vue'
import Reader from '../components/reader.vue'

const history = createWebHistory();
const router = createRouter({
    history: history,
    routes: [
        {
            path: '/',
            name: 'Home',
            component: Home
        },
        {
            path: '/searchresult',
            name: 'Searchresult',
            component: searchResult
        },
        {
            path: '/signup',
            name: 'Signup',
            component: SignUp
        },
        {
            path: '/login',
            name: 'LogIn',
            component: LogIn
        },
        {
            path: '/book',
            name: 'Paper',
            component: Paper
        },
        {
            path: '/reader',
            name: 'Reader',
            component: Reader
        },
    ]
});

export default router