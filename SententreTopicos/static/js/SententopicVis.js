/*
    var graph = {
        "nodes": [
            { "name": "jhorel", "width": 60, "height": 40 },
            { "name": "bebe", "width": 60, "height": 40 },
            { "name": "casa", "width": 60, "height": 40 },
            { "name": "dedo", "width": 60, "height": 40 },
            { "name": "enano", "width": 60, "height": 40 }
        ],
        "links": [
            { "source": 0, "target": 2 },
            { "source": 2, "target": 1 },
            { "source": 2, "target": 3 },
            { "source": 1, "target": 4 }
        ],
        "constraints": [
            {
                "type": "alignment",
                "axis": "x",
                "offsets": [
                    { "node": 1, "offset": 0 },
                    { "node": 3, "offset": 0 }
                ]
            }
        ]
    };
    */


var escogidos = [];

//------------------------------
const width = document.querySelector("#sententreeTopicos").offsetWidth;
const height = document.querySelector("#sententreeTopicos").offsetHeight;

const d3cola = cola.d3adaptor()
    .avoidOverlaps(true)
    .size([width, height]);


let escalaFuente=d3.scale.linear()
    .domain([0,graph.maxSize])
    .range([10,200]);

// var detalles=d3
//     .select('#interacciones')
//     .append('div')
//     .attr('class','detalles')
//     .attr('id','tooltip')
//     .style('position','relative ')
//     .style('opacity',0);

var detalles = d3
    .select('.detalles');

const svg = d3
    .select("#sententreeTopicos")
    .append("svg")
    .attr("class", "main")
    .attr("width", width)
    .attr("height", height);

var colors = ["#f94144", "#f3722c", "#f8961e", "#f9844a", "#9f86c0", "#90be6d", "#43aa8b", "#4d908e", "#577590", "#277da1"];
var filterDef = svg.append("defs");
var filter = filterDef
    .append("filter")
    .attr("x", "0")
    .attr("y", "0")
    .attr("width", "1")
    .attr("height", "1")
    .attr("id", "solid");

filter.append("feFlood")
    .attr("flood-color", "white")
    .attr("result", "bg");

var filterMerge = filter.append("feMerge");

filterMerge.append("feMergeNode")
    .attr("in", "bg");

filterMerge.append("feMergeNode")
    .attr("in", "SourceGraphic");


/*
var domain=createDomain(100,colors.length)
var color=d3
    .scale.linear()
    .domain(domain)
    .range(colors);

function createDomain(dataLength,colorsLength){
    var domain = [0];
    var toAdd = colorsLength - 2;
    for(i = 1; i <= toAdd; i++) {
        domain.push(Math.floor(dataLength * (i / (colorsLength - 1))));
    }
    domain.push(dataLength - 1);         
    return domain;
}
*/
function renderLinks() {
    var link = svg
        .selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke", (d, i) => {
            if (d.tipo == "sententopic")
                return "#bbbbbb";
            //return "black";
            return colors[(d.source.numTopic % 10)]
        })
        .style("stroke-width", (d, i) => {
            if (d.tipo == "sententopic")
                return "5px";
            return "1px";
        })
        .call(d3cola.drag);
    return link;
}
function renderNodes() {
    var node = svg
        .selectAll(".node")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", (d, i) => {
            if (d.label == " ") {
                // return 15;
                return 15;
            }
            return 0;
        })
        .call(d3cola.drag);
    //.style("stroke", "#bbbbbb")
    //.style("stroke-width", "5px");
    return node;
}
function renderLabels() {
    var label = svg
        .selectAll(".label")
        .data(graph.nodes)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr('dy', '.28em')
        .attr('index', (d, i) => i)
        .text(function (d) { return d.label; })
        //.style("filter","url(#solid)")
        .style("font-size", (d) => {
            // return d.fontSize + "%"; 
            return escalaFuente(d.fontSize);
        })
        .style("font-weight", "bolder")
        .style("fill", (d, i) => {
            return colors[(d.numTopic % 10)];
        })
        .on('mouseover', mouseEncima)
        .on('mouseout', mouseAfuera)
        .call(d3cola.drag);

    label.append("title").text(function (d) { return d.rawText; });

    return label;
}
function renderGroups() {
    var group = svg.selectAll(".group")
        .data(graph.groups)
        .enter()
        .append("rect")
        .attr("rx", 8).attr("ry", 8)
        .attr("class", "group")
        .style("stroke-width", 3)
        //.style("stroke", "rgb(0,0,0)")
        .style("stroke", (d, i) => {
            return colors[(d.grupo % 10)];
        })
        .style("stroke-dasharray", 10)
        //.style("fill-opacity", "0.0")
        .style("fill", "#f8f9fa")
        .on('click', function (d, i) {
            if (escogidos.includes(d.grupo)) {
                const index = escogidos.indexOf(d.grupo);
                escogidos.splice(index, 1);
                console.log(escogidos);
                d3
                    .select(this)
                    .style("stroke", (d, i) => {
                        return colors[(d.grupo % 10)];
                    })
                    .style("fill", "white")
                    .style("fill-opacity", "1");
            }
            else {
                escogidos.push(d.grupo);
                console.log(escogidos);
                d3
                    .select(this)
                    .style("stroke", "rgb(125,0,0)")
                    .style("fill", "rgb(125,0,0)")
                    .style("fill-opacity", "0.25");
            }
        })
        .call(d3cola.drag);

    return group;
}

function mouseEncima(event, d) {
    detalles.style('opacity', 0.92);
    var i = this.getAttribute('index');
    detalles
        .html(
            '🐦 Tweet: <b>' + graph.nodes[i].rawText + '</b> <br>❤️ Likes: '+graph.nodes[i].likes_count
        )
        // .style('left', 260 + 'px')
        // .style('top', 0 + 'px')
        .style('background-color', function () {
            return '#ade8f4';
        });
}

function mouseAfuera(data) {
    detalles
        .style('opacity', 0)
    // .style('left', -1 + 'px')
    // .style('top', -3 + 'px');
}
function update() {
    console.log(graph);
    d3cola
        .nodes(graph.nodes)
        .links(graph.links)
        .groups(graph.groups)
        .constraints(graph.constraints)

        .flowLayout('x', 120)
        //.linkDistance((d,i)=>{return d.length;})
        //.linkDistance(70)
        .jaccardLinkLengths((d, i) => { return d.length; })
        .start();

    var oldLinks = svg.selectAll(".link").remove();
    var oldLabel = svg.selectAll(".label").remove();
    var oldGroup = svg.selectAll(".group").remove();
    var oldNode = svg.selectAll(".node").remove();
    /****crear nodos,links y grupos****/
    const group = renderGroups();
    const link = renderLinks();
    const node = renderNodes();
    const label = renderLabels();


    /****Actualizar Nodos****/
    var d3Nodes = document.querySelectorAll(".label");
    const bboxNodes = [];
    for (let i = 0; i < d3Nodes.length; i++) {
        if (graph.nodes[i].label == " ") {
            // console.log("entre");
            /*
            var circleBbox=node[0][i].getBBox();
            graph.nodes[i].height = circleBbox.height;
            graph.nodes[i].width = circleBbox.width;
            */
            graph.nodes[i].height = 90;
            graph.nodes[i].width = 60;
            continue;
        }
        var labelBbox = d3Nodes[i].getBBox();
        bboxNodes.push(labelBbox);
        //console.log(labelBbox);
        graph.nodes[i].height = labelBbox.height + 2.0;
        graph.nodes[i].width = labelBbox.width + 2.0;
    }

    /****d3 tick****/
    d3cola.on("tick", function () {
        var groupGap = 5;
        label
            .attr("x", function (d) {
                var w = this.getBBox().width;
                return d.x - w / 2;
                //return d.x;
            })
            .attr("y", function (d) {
                var h = this.getBBox().height;
                return d.y;
            });
        //------------------------------------
        node
            .attr("cx", (d) => {
                if (d.label == " ") {
                    // return d.x+14;
                    return d.x;
                }
                return d.x;
            })
            .attr("cy", (d) => {
                return d.y;
            })
        //------------------------------------
        link
            .attr("x1", function (d, i) {
                /*if(d.target.x>d.source.x){
                    console.log(d.target);
                    return d.source.x+(anchos[i]/2)+gap;
                }
                else{
                    return d.source.x-(anchos[i]/2)-gap;
                }*/
                if (d.tipo == "sententopic") {
                    //return d.target.x;
                    //return d.target.parent.bounds.x+(d.target.parent.bounds.width()/2);
                    if (!d.source.parent) {
                        //NODO CENTRAL
                        return d.source.x;
                    }
                    //LOS DEMAS NODOS
                    return d.source.parent.bounds.X;
                }
                return d.source.x + (d.source.width / 2);
            })
            .attr("y1", function (d, i) {
                return d.source.y;
            })
            .attr("x2", function (d, i) {
                /*if(d.target.x>d.source.x){
                    return d.target.x-(anchos[i*2]/2)-gap;
                }
                else{
                    return d.target.x+(anchos[i*2]/2)+gap;
                }*/
                if (d.tipo == "sententopic") {
                    //return d.target.x;
                    //return d.target.parent.bounds.x+(d.target.parent.bounds.width()/2);
                    if (!d.target.parent) {
                        return d.target.x;
                    }
                    return d.target.parent.bounds.x;
                }
                return d.target.x - (d.target.width / 2);
            })
            .attr("y2", function (d) {
                return d.target.y;
            });
        //------------------------------------
        group.attr("x", function (d) {
            return d.bounds.x;
        })
            .attr("y", function (d) {
                return d.bounds.y;
            })
            .attr("width", function (d) {
                return d.bounds.width();
            })
            .attr("height", function (d) {
                return d.bounds.height();
            });
    });
}

// Main 
update();

    /*
document.querySelector("#sententreeTopicos").offsetHeight;

var width = document.querySelector("#sententreeTopicos").offsetWidth;
height = document.querySelector("#sententreeTopicos").offsetHeight;


var d3cola = cola.d3adaptor()
    .avoidOverlaps(true)
    .size([width, height]);

var svg = d3
    .select("#sententreeTopicos")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

d3cola
    .nodes(graph.nodes)
    .links(graph.links)
    .constraints(graph.constraints)
    .flowLayout('x', 90)
    .linkDistance(90)
    .jaccardLinkLengths(1)
    .start(10, 10, 10);


var link = svg.selectAll(".link")
    .data(graph.links)
    .enter().append("line")
    .attr("class", "link")
    .style("stroke", "red");

var node = svg
    .selectAll(".node")
    .data(graph.nodes)
    .enter()
    .append("rect")
    .attr("class", "node")
    .attr("width", function (d) {
        var sizePalabra = d.name;
        return sizePalabra.length * 10.5;
    })
    .attr("height", function (d) {
        var sizePalabra = d.name;
        return sizePalabra.length * 4;
    })
    .style("fill", "white")
    .style("stroke-width", "2")
    .style("stroke", "white")
    .call(d3cola.drag);


var label = svg
    .selectAll(".label")
    .data(graph.nodes)
    .enter()
    .append("text")
    .attr("class", "label")
    .attr('dy', '.28em')
    .text(function (d) { return d.name; })
    .style("font-size", (d) => { return 100 + "%"; })
    .style("font-weight", "bold")
    .call(d3cola.drag);


//.call(d3cola.drag);

label.append("title").text(function (d) { return d.name; });


d3cola.on("tick", function () {
    link.attr("x1", function (d) {
        return d.source.x;
    })
        .attr("y1", function (d) {

            return d.source.y;
        })
        .attr("x2", function (d) {
            var w = this.getBBox().width;
            return d.target.x;
        })
        .attr("y2", function (d) {
            return d.target.y;
        });

    node.attr("x", function (d) {
        var w = this.getBBox().width;
        //return d.x - d.width / 2; 
        return d.x - w / 2;
    })
        .attr("y", function (d) {
            var h = this.getBBox().height;
            //return d.y - d.height / 2; 
            return d.y - h / 2;
        });

    label.attr("x", function (d) {
        var w = this.getBBox().width;

        return d.x - w / 2;

    })
        .attr("y", function (d) {
            var h = this.getBBox().height;
            return d.y;
        });

});
*/