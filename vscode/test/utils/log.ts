
export function getLogger(prefix?: string) {
    return function (msg: string, ...xtras: any[]) {
        console.log(`${prefix}: ${msg}`);
    }
}
