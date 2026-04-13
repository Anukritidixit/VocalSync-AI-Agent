let listExample = [1, 2, 3];
listExample.push(4);
console.log(listExample);

let tupleExample = [1, 2, 3];
// tupleExample.push(4); // This would work in JavaScript, but it's not a true tuple like in Python
Object.freeze(tupleExample);
console.log(tupleExample);