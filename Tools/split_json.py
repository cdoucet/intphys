#!/usr/bin/env python3


import argparse
import json
import os


def balance_int(l, n):
    if l == n:
        L = [1] * n
    if l < n:
        L = [1] * l + [0] * (n-l)
    else:
        L = [int(l / n) for _ in range(n-1)]
        L = [l - sum(L)] + L

    assert sum(L) == l
    assert len(L) == n
    return L


def balance_list(L, n):
    idx = list(range(n))
    M = [[] * n] * len(L)
    for i, l in enumerate(L):
        B = balance_int(l, n)
        M[i] = [B[k] for k in idx]
        idx = [idx[-1]] + idx[:-1]

    assert len(M) == len(L)
    assert all(len(M[i]) == n for i in range(len(L)))
    assert all(sum(M[i]) == L[i] for i in range(len(L)))
    M = [list(a) for a in zip(*M)]
    return [m for m in M if sum(m)]


def unroll_dict(D, head=[]):
    keys, values = [], []
    for k, v in D.items():
        k = head + [k]
        if isinstance(v, dict):
            K, V = unroll_dict(v, head=k)
            keys += K
            values += V
        else:
            keys += [k]
            values += [v]
    return keys, values


def roll_dict(keys, values):
    def _aux(k, v):
        if len(k) == 1:
            return {k[0]: v}
        else:
            return {k[0]: _aux(k[1:], v)}

    L = [_aux(k, v) for k, v in zip(keys, values)]

    D = {}
    for l in L:
        for k, v in l.items():
            if k in D:
                D[k] += [v]
            else:
                D[k] = [v]

    # E = {}
    # for k, v in D.items():
    #     if isinstance(v, list):
    #         for d in v:
    #             for k, vv in d.items():
    #                 if k not in E:
    #                     E[k] = {}
    #                 E[k].update(vv)
    #     else:
    #         E[k] = v
    #         # k: vv for d in v for k, vv in d.items()}
    return D


def split_json(input_json, n, output_dir):
    """Split the workload one one json into `n` ones"""
    input_json = json.load(open(input_json, 'r'))
    print(input_json)
    keys, values = unroll_dict(input_json)
    configs = balance_list(values, n)

    for i, config in enumerate(configs, start=1):
        assert len(keys) == len(config)
        d = roll_dict(keys, config)
        output_json = os.path.join(output_dir, f'{i}.json')
        open(output_json, 'w').write(json.dumps(d) + '\n')
        print(json.dumps(d))


def main():
    parser = argparse.ArgumentParser(
        'Split a JSON of scenes descriptions into balanced subparts')

    parser.add_argument('json_file', help='the input JSON file to split')
    parser.add_argument('n', type=int, help="the number of splits to generate")
    parser.add_argument('output_dir', help='directory where to write JSONs')

    args = parser.parse_args()

    split_json(args.json_file, args.n, args.output_dir)


if __name__ == '__main__':
    main()
