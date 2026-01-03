window.addEventListener('load', function () {
        if (!window.jQuery) {
            return;
        }
        var listEl = document.getElementById("category-list");
        if (!listEl) {
            return;
        }
        var categoryUrl = listEl.dataset.categoryUrl;
        var blogHomeUrl = listEl.dataset.blogHomeUrl;
        $.getJSON(categoryUrl, function (data) {
            var categories = data.results || data;
            var $list = $("#category-list");
            $list.empty();

            categories.forEach(function (cat) {
                var link = blogHomeUrl + "?categories=" + encodeURIComponent(cat.id);
                $list.append('<li><a href="' + link + '">' + cat.name + '</a></li>');
            });
        });
    });
