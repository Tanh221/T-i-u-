from ortools.linear_solver import pywraplp
import time


def Input():
    [n, k] = [int(x) for x in sys.stdin.readline().split()]
    d = []
    for i in range(2 * n + 1):
        r = [int(x) for x in sys.stdin.readline().split()]
        d.append(r)
    return n, k, d


def data(n, k, dis):
    data = {}
    data["n"] = n
    data["k"] = k
    data["distance"] = dis
    return data


def linear_solve():
    solver = pywraplp.Solver.CreateSolver("SAT")
    n, k, dis = Input()
    start = time.time()
    x = {}
    u = {}
    u[0] = 0
    index = {}

    for i in range(2 * n + 1):
        for j in range(2 * n + 1):
            if i != j:
                x[i, j] = solver.IntVar(0, 1, "x(" + str(i) + ", " + str(j) + ")")

    for i in range(1, n + 1):
        u[i] = solver.IntVar(1, k, "k(" + str(i) + ")")

    for i in range(n + 1, 2 * n + 1):
        u[i] = solver.IntVar(0, k - 1, "k(" + str(i) + ")")

    for i in range(1, 2 * n + 1):
        index[i] = solver.IntVar(1, 2 * n, "index of point " + str(i))

    # CONSTRAINT 1: each point visit by only 1 point and from each point move to exactly 1 point
    for i in range(2 * n + 1):
        solver.Add(sum(x[i, j] for j in range(2 * n + 1) if i != j) == 1)
        solver.Add(sum(x[j, i] for j in range(2 * n + 1) if i != j) == 1)

    # CONSTRAINT 2: pick when move to a pick up point
    for i in range(2 * n + 1):
        for j in range(1, n + 1):
            if i != j:
                solver.Add(10000 * (1 - x[i, j]) + u[i] - u[j] >= -1)
                solver.Add(10000 * (1 - x[i, j]) + u[j] - u[i] >= 1)

    # CONSTRAINT 3: drop when move to a drop off point
    for i in range(1, 2 * n + 1):
        for j in range(n + 1, 2 * n + 1):
            if i != j:
                solver.Add(10000 * (1 - x[i, j]) + u[i] - u[j] >= 1)
                solver.Add(10000 * (1 - x[i, j]) + u[j] - u[i] >= -1)

    # CONSTRAINT 4: can not return to point 0 from a pick up point
    # and can not move to a drop off point from start point 0
    for i in range(1, n + 1):
        solver.Add(x[i, 0] == 0)

    for i in range(n + 1, 2 * n + 1):
        solver.Add(x[0, i] == 0)

    # CONSTRAINT 5: index of a pick up point < index of its corresponding drop off point
    # use slack variable h to change from ">" to ">="
    h = solver.IntVar(1, 100, "h")
    for i in range(1, n + 1):
        solver.Add(index[i + n] - index[i] - h >= 0)

    # CONSTRAINT 6: x[i,j] = 1 then index[j] > index[i]
    for i in range(1, 2 * n + 1):
        for j in range(1, 2 * n + 1):
            if i != j:
                solver.Add(10000 * (1 - x[i, j]) + index[j] - index[i] - h >= 0)

    obj = sum(
        x[i, j] * data(n, k, dis)["distance"][i][j]
        for i in range(2 * n + 1)
        for j in range(2 * n + 1)
        if i != j
    )
    solver.Minimize(obj)
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print(n)
        count = 1
        current_point = 0
        while count <= 2 * n:
            i = current_point
            for j in range(2 * n + 1):
                if i != j and x[i, j].solution_value() == 1:
                    print(j, end=" ")
                    current_point = j
                    count += 1
        print(solver.Objective().Value())
        end = time.time()
        print(end - start)


linear_solve()
