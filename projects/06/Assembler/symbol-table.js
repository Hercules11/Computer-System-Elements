// 初始化符号表
const table = {}
let ramAddress = 16
table.SP = 0
table.LCL = 1
table.ARG = 2
table.THIS = 3
table.THAT = 4
table.SCREEN = 16384
table.KBD = 24576

let num = 16
let key
// R0 - R15赋值
//ES6 模板字符串(Template String)是增强版的字符串，用反引号(`)标识，它可以当作普通字符串使用，也可以用来定义多行字符串，或者在字符串中嵌入变量。
while (num--) {
    key = `R${num}`
    table[key] = num
}

// 将符号添加到表
// 为table对象添加符号-地址对
function addEntry(symbol, address) {
    table[symbol] = address
}
// 表是否包含符号
function contains(symbol) {
    return table[symbol] !== undefined? true : false
}

function getAddress(symbol) {
    return table[symbol]
}

//向外暴露函数，对象，和变量
module.exports = {
    table,
    ramAddress,
    addEntry,
    contains,
    getAddress,
}
//此文件完成了符号表的初始化，以及相关操作函数（添加，获取地址， 判断是否存在）的建立