require.config({
    baseUrl: '../static/js/lib',
    paths:{
        'jquery': 'jquery.min',
        'd3': 'd3.min'
    }
});

require(['jquery', 'd3'], function($, d3){
    var data_temp;
    $.ajax({
        url: "post",
        type: "POST",
        dataType: "json",
        async: false,
        success: function(d) {
            data_temp = d;
        }
    })
    // console.log(typeof(data_temp), data_temp);

    function array_equal(a, b) {
        if(a.length != b.length) {
            return false;
        }
        for(var i=0; i<a.length; i++) {
            if(a[i] != b[i]) {
                return false;
            }
        }
        return true;
    }

    //获取元素在数组的下标
    Array.prototype.indexOf = function(val) {
        for (var i = 0; i < this.length; i++) {
            if (array_equal(this[i], val)) { 
                return i;
            };
        }
        return -1; 
    };

    //根据数组的下标，删除该下标的元素
    Array.prototype.remove = function(val) {
        var index = this.indexOf(val);
        if (index > -1) {
        this.splice(index, 1);
        }
    };

    function render_submit() {
        d3.select(".vis")
            .append("input")
            .attr("type", "button")
            .attr("value", "保存")
            .on("click", function(d) {
                $.ajax({
                    url: "save",
                    type: "POST",
                    dataType: "json",
                    async: false,
                    success: function(d) {
                        if(d["CODE"] == 200) {
                            alert("保存成功");
                        }
                    }
                })
            })
    }

    function render(data) {
        d3.select(".vis")
            .append("div")
            .style("border-top", "2px solid lightgrey")
            .attr("class", "seg" + data["id"])
            .style("margin", "12px 5px")
            
        
        var sent = d3.select(".seg" + data["id"])
            .append("div")

        
            

        sent.append("div")
            .attr("class", "subjects")
            .text(" <" + data['subjects'] + "> ")
            .style("color", "red")
            .style("float", "left")

        sent.append("div")
            .attr("class", "sentence")
            .text(" " + data["id"] + " -- " + data['sentence'])

        // d3.select(".seg" + data["id"])
        //     .append("div")
        //     .attr("class", "subjects")
        //     .text()
        //     .style("color", "red")

        
        var pos = d3.select(".seg" + data["id"])
            .append("div")
            .style("overflow", "auto")
            .selectAll("div")
            .data(data["tuples"])
            .enter()
            .append("div")
            .attr("class", "pos")
            .style("margin", "0 10px 0 0")
            .style("float", "left")

        d3.select(".seg" + data["id"])
            .select("div")
            .append("div")


        pos.text(
            function(d) {
                return d[0] + "-" + d[3];
            })
            .style("color", function(d) {
                if(d[2] == "nsubj") {
                    return "blue";
                }
            })
            .append("input")
            .attr("type", "checkbox")
            .on("click", function(d, i) {
                if(this.checked) {
                    data['tokens'].push([i, d[0], d[3]]);
                }
                else {
                    data['tokens'].remove([i, d[0], d[3]]);

                }
            })


        d3.select(".seg" + data["id"])
            .append("form")
            .style("float", "left")
            .style("margin", "0 50px 0 0")
            .style("border", "1px solid lightgrey")
            .selectAll("radio")
            .data(["None", "N", "NR"])
            .enter()
            .append("label")
            .style("margin", "0 10px")
            .text(function(d) {
                return d;
            })
            .append("input")
            .attr("type", "radio")
            .attr("name", "type")
            .on("click", function(d) {
                data['type'] = d;
            })

         d3.select(".seg" + data["id"])
            .append("form")
            .style("float", "left")
            .style("margin", "0 50px 0 0")
            .style("border", "1px solid lightgrey")
            .selectAll("radio")
            .data(["False", "PartialTrue", "True"])
            .enter()
            .append("label")
            .style("margin", "0 10px")
            .text(function(d) {
                return d;
            })
            .append("input")
            .attr("type", "radio")
            .attr("name", "check")
            .on("click", function(d) {
                data['validity'] = d;
            })
        
        
        d3.select(".seg" + data["id"])
            .append("input")
            .attr("type", "button")
            .attr("value", "提交")
            .on("click", function(d) {
                data["is_process"] = "is_process";
                if(!data['type']) {
                    data['type'] = 'not_select';
                }
                $.ajax({
                    url: "result",
                    type: "POST",
                    dataType: "json",
                    data: JSON.stringify(data),
                    async: false,
                    success: function(d) {
                        console.log(data['subjects'])
                        if(d["CODE"] == 200) {
                            d3.select(".label" + data["id"])
                                .text("  --已提交")
                        }
                    }
                })
            })
        
        d3.select(".seg" + data["id"])
            .append("label")
            .attr("class", "label" + data["id"])
            .style("opacity", 0.5)
    }
    function main() {
        render_submit();
        for(var k in data_temp) {
            if(!data_temp[k]['is_process']) {
                render(data_temp[k]);
            }
        }
        render_submit();
    }

    main()

});