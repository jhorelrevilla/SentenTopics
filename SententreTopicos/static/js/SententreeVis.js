class SententreeVis {
    constructor(data, height, width, container) {
        this.data = data
        this.svgBC = d3
            .select(container)
            .append('svg')
            .attr('height', height)
            .attr('width', width);
        //this.renderTree(data,heigh)
    }
    renderNodes() {

    }

    renderlinks() {

    }

    renderTree(data, height, width) {
        return None;
    }
}

function xd() {
    this.container = d3.create("svg");
    container
        .append('text')
        .text("XD")
        .attr("x", 20)
        .attr("y", 20);
}
function XD1(msg) {
    console.log(msg);
}

/*console.log(data.nodes[0].id)
console.log(document.querySelector(".sententreeTopico1").offsetHeight)
console.log(window.innerWidth)
*/
//const arbol=new SententreeVis("xd",20,20,'body');

