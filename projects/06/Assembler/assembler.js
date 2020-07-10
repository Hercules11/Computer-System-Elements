const table = require('./symbol-table')
const fs = require('fs')
const parser = require('./parser')

//process.argv 属性会返回一个数组，其中包含当 Node.js 进程被启动时传入的命令行参数。 第一个元素是 process.execPath。 如果需要访问 argv[0] 的原始值，则参见 process.argv0。 第二个元素是正被执行的 JavaScript 文件的路径。 其余的元素是任何额外的命令行参数。
//啥意思
let fileName = process.argv[2]
//读文件
fs.readFile(fileName, 'utf-8', (err, data) => {
    if (err) {
        throw err
    }
    // 每行指令
    //'\r'是回车，前者使光标到行首，（carriage return）
// '\n'是换行，后者使光标下移一格，（line feed）
// \r 是回车，return
// \n 是换行，newline
// 对于换行这个动作，unix下一般只有一个0x0A表示换行("\n")，windows下一般都是0x0D和0x0A两个字符("\r\n")，苹果机(MAC OS系统)则采用回车符CR表示下一行(\r)
// Unix系统里，每行结尾只有“<换行>”，即“\n”；
// Windows系统里面，每行结尾是“<回车><换行>”，即“\r\n”；
// Mac系统里，每行结尾是“<回车>”,即“\r”。
    data = data.split('\r\n')

    // 首次解析收集符号
    //啥意思
    parser([...data], true)

    // 真正的解析指令
    const binaryOut = parser(data)

    fileName = fileName.split('.')[0]
//写出文件，文件名，数据
// x => x * x
// 上面的箭头函数相当于：
// function (x) {
//     return x * x;
// }
    fs.writeFile(fileName + '.hack', binaryOut, (err) => {
        if (err) {
            throw err
        }
    })
})
