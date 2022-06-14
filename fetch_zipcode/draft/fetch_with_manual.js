// import: https://code.jquery.com/jquery-3.6.0.min.js

// page:http://postcode.info
var a_arr = $(".cnt table tbody tr td a")
a_arr.each(function (index, a) {
    var text = $(a).text().replace("\n", "")
    var href = $(a).attr("href")
    console.log(text + "," + href)
})

// page:http://china.postcode.info/
var a_arr = $(".cnt a")
a_arr.each(function (index, a) {
    var text = $(a).text().replace("\n", "")
    var href = $(a).attr("href")
    console.log(text + "," + location.href + href)
})

// page:http://china.postcode.info/beijing/
var a_arr = $(".cnt .letterbutton a")
a_arr.each(function (index, a) {
    var text = $(a).text().replace("\n", "")
    var href = $(a).attr("href")
    console.log(text + "," + location.href + href)
})

// page:http://china.postcode.info/beijing/c
var a_arr = $(".cnt table tbody tr td a")
a_arr.each(function (index, a) {
    var text = $(a).text().replace("\n", "")
    var href = $(a).attr("href")
    var url = location.href + href
    console.log(text + "," + href)
    $.get(url, function (data) {
        var first_p = $(data).find(".shell .container p")[0]
        console.log($(first_p).find("a strong").text())
    })
})