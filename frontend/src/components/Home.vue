<template>
    <div id="app-wrapper" style="display: flex; flex-direction: column; min-height: 100vh;">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a href="/"><img src="../assets/img/logo-B.png" alt="LOGO" style="width: 35px !important;"></a>
                &nbsp;&nbsp;&nbsp;
                <a class="navbar-brand" href="./"><i class="mr-2"></i><span style="font-weight: bold">Book</span>
                    hub</a>
                <button class="navbar-toggler collapsed" type="button" data-toggle="collapse"
                    data-target="#navbarColor02" aria-controls="navbarColor02" aria-expanded="false"
                    aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="navbar-collapse collapse" id="navbarColor02" style="">
                    <ul class="navbar-nav mr-auto d-flex align-items-center">
                        <li class="nav-item">
                            <a class="nav-link" href="./" style="font-weight: none; font-size: 15px">首页</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="./searchresult?field=recommend&info=%20"
                                style="font-weight: none; font-size: 15px">发现</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav ml-auto d-flex align-items-center">
                        <li class="nav-item">
                        </li>
                    </ul>
                </div>


                <ul class="navbar-nav ml-auto d-flex align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="./reader" style="font-weight: none; font-size: 15px">我的书架</a>
                    </li>
                    <li v-if="!this.isLogin" class="nav-item">
                        <span class="nav-link">
                            <a class="btn btn-secondary btn-round fade-down-left" href="/signup">注册</a>&nbsp;
                            <a class="btn btn-secondary btn-round " href="/login">登录</a>
                        </span>
                    </li>
                    <li v-else class="nav-item">
                        <span class="nav-link">
                            <a class="btn btn-outline-primary btn-round fade-down-left"
                                style="color:#c3a6cb !important; border-color: #c3a6cb !important;" @click="logOut">登出</a>
                        </span>
                    </li>
                </ul>


            </div>
        </nav>

        <div class="jumbotron jumbotron-lg jumbotron-fluid mb-0 bg-primary position-relative up_padding_small"
            style="flex-grow: 1; display: flex; flex-direction: column;">
            <div class="container text-white h-100 tofront d-flex flex-column justify-content-center">
                <!-- <img src="https://z1.ax1x.com/2023/11/02/piK4OA0.png" :width="300"> -->
                <h1 class="middle_title">
                    <!-- NOODLE SCHOLAR <i class="mr-4"></i> -->
                    <img src="../assets/img/bookhub.png" :width="300">
                    <!-- <i class="mr-4"></i> 开搜未来 -->
                </h1>
                <br><br>
                <!-- <h1 class="display-4 middle_title">唯一的不同，<br><span class="font-weight-bold">是处处都不同。</span></h1><br> -->

                <div class="row align-items-center justify-content-center text-center">
                    <div class="col-md-7 ">

                        <!-- 上方 -->
                        <div class="input-group under_border form-check-input reform_margin">

                            <!-- 搜索框 -->
                            <input id="search-input" type="text" class="form-control form-control-rounded no_box_shadow"
                                v-model="search_info" @keyup.enter="SearchAndGoToResultPage"
                                aria-label="Text input with dropdown button" :placeholder="`Search by ${search_type}`">

                            <!-- 搜索条件选择器 -->
                            <div class="input-group-append">
                                <button class="btn btn-outline-secondary_rewrite dropdown-toggle btn-rounded"
                                    type="button" data-toggle="dropdown" aria-expanded="false">{{ search_type
                                    }}</button>
                                <div class="dropdown-menu">
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Recommend')"><strong>Recommend</strong></a>
                                    <div role="separator" class="dropdown-divider"></div>
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Title')"><strong>Title</strong></a>
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Author')"><strong>Author</strong></a>
                                </div>
                            </div>
                        </div>


                        <!-- 下方 -->
                        <!-- 搜索按钮 -->
                        <div class="row col-md-13 reform_margin">
                            <button type="button" @click="SearchAndGoToResultPage"
                                class="btn btn-primary btn-lg btn-block btn-rounded button_white_border_home">Search</button>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- <section class="pt-3 pb-4" data-aos="zoom-in">
        <div class="container text-center">
            <div class="row justify-content-center">
                <div class="col-md-10">
                    <p>zoom-in Screen shot 1</p>
                    <img class="d-block m-auto" src="../assets/img/demo/screenshot1.png" alt="">
                </div>
            </div>
        </div>
    </section> -->

    <!-- 
    <div class="jumbotron jumbotron-fluid no_under_margin">
        <div class="container">
            <h1 class="display-4 text-right">虽然轻，<br>但<span class="font-weight-bold">代码</span>分量<span
                    class="font-weight-bold">重。</span></h1>
            <p class="lead text-left">
                5个人8个分支，无用代码与有用代码共同管理。<br>
                大小驼峰随意使用，<br>
                <span class="font-weight-bold">生怕你看得懂。</span>
            </p>
        </div>
    </div>


    <div class="jumbotron jumbotron-fluid no_under_margin">
        <div class="container">
            <h1 class="display-4 text-left">全新用户登录协议，<br><span class="font-weight-bold">只许协，<br>不许议。</span></h1>

            <p class="lead text-right">

            </p>
        </div>
    </div>

    <div class="jumbotron jumbotron-fluid no_under_margin">
        <div class="container">
            <h1 class="display-4 text-right">你的下一个搜索引擎，<br><span class="font-weight-bold">何必是你的。</span></h1>
            <p class="lead text-left">
                用户信息完全泄漏，搜索记录数据库可见。<br><span class="font-weight-bold">你的隐私，我说了算。</span>
            </p>
        </div>
    </div> -->
</template>


<script>
// 6532290ad507ea15ca185e7f
// arxiv: 6569d4442c9d068894e2ac4c
import axios from 'axios';
import * as echarts from 'echarts';
// import echarts from 'echarts';
// Vue.prototype.$echarts = echarts;

export default {
    data() {
        return {
            isLogin: false,

            component_title: "get Requset",
            already_searched: false,
            paper_id: "NULL id",
            paper_name: "NULL name",

            search_type: "Recommend",
            search_type_print: "recommend",
            search_info: "",
        };
    },

    async mounted() {
        await this.initialize();
    },


    methods: {
        async initialize() {
            await this.checkLogin();
            $(this.$el).find('[data-toggle="dropdown"]').dropdown();
        },

        async checkLogin() {
            return axios.get('http://10.80.158.19:8088/api/v1/user/check_login')
                .then((response) => {
                    this.isLogin = response.data.login_in;
                    console.log("log in status: " + response.data.login_in);
                })
                .catch((error) => {
                    console.log(error);
                })
        },

        SearchAndGoToResultPage() {
            var url = "/searchResult?field=" + (this.search_type).toLowerCase() + "&info=" + encodeURIComponent(this.search_info);
            this.$router.push(url);
        },

        selectSearchType(type) {
            this.search_type = type;
            this.$nextTick(() => {
                $(this.$el).find('[data-toggle="dropdown"]').dropdown('update');
            });
            console.log("search_type changed to " + type);
            console.log("search_type_print: " + type);
        },

        async logOut() {
            axios.get('http://10.80.158.19:8088/api/v1/user/logout')
                .then((response) => {
                    console.log("log out status: " + response.data.logout);
                    this.isLogin = false;

                })
                .catch((error) => {
                    console.log(error);
                });
            await this.initialize();
        }
    },

    watch: {

    },

    computed: {

    },
};
</script>

<!-- 额外样式 -->
<style>
[v-cloak] {
    display: none;
}

.up_padding_small {
    padding-top: 130px;
}

.middle_title {
    text-align: center !important;
}

.under_border {
    border-bottom: 10px solid #502c6c;
}

.no_under_margin {
    margin-bottom: 0;
}

.display_inline {
    display: inline-block !important;
    /* 或者 display: inline-block; */
}

.btn-rounded {
    border-radius: 20px;
}

.button_white_border_home {
    border-color: #ffffff;
}

.form-control-rounded {
    border-radius: 20px;
}

.search_button_color {
    background-color: #1b54f2;
}

.btn-outline-secondary_rewrite {
    color: #7832e2;
    background-image: none;
    font-weight: bold;
}

.btn_circle_home {
    width: 60px !important;
    height: 38.797px !important;
    border-radius: 20px 0 0 20px !important;
    position: relative !important;
    padding: 0 !important;
    overflow: inherit !important;
    border: none !important;
    background-color: #ffffff;
    color: #7832e2;
}

.btn_circle_home_active {
    background-color: #7832e2 !important;
    color: #ffffff !important;
}

.btn_circle:hover {
    background-color: #7832e2 !important;
}

.no_box_shadow {
    box-shadow: none !important;
}

.reform_margin {
    margin: auto;
}

.home_table_title {
    color: #e9e7ef;
    font-weight: bold;
    border: #e9e7ef 3px solid;
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: 20px;
}

.my_nav {
    color: #000000;
    font-weight: bold;
}

.home_table_container {
    background-color: #725e82;
    border: 2px solid #e3f9fd;
    border-radius: 10px;
    padding: 20px;
}
</style>