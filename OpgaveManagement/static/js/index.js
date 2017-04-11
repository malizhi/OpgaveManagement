/**
 * Created by malizhi on 2017/3/25.
 */

    var bookList = [];
   $(function () {
       setCsrftoken();
       var $width = $(window).width();
       $(".indexView").css({width:$width - 60, marginLeft:"auto", marginRight:"auto"});
       $(".mybookList ul li").each(function(){
           var $chiden = $(this).children();
           if ($chiden.length  == 2){
               $chiden.eq(0).css({width:$(this).width() - $chiden.eq(1).innerWidth() - 10});
           }else {
               $chiden.eq(0).css({width:$(this).width()});
           }
       });

   function getMoreBook() {
       // 获取更多图书
   }

   function getAllRecommendAutour(){
       // 查看全部的推荐的作者
   }

   function  getBook() {
       //获取书籍的信息
   }
   
   function  getAuthor() {
       // 获取推荐的作者
   }
   
   function attention() {
       // 关注
       
   }
   
   function comment() {
       // 评论
   }
   
   function collect() {
       // 收藏
   }

});











