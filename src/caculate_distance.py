from __init__ import *

class CaculateDistance(object):
    def __init__(self):
        self.angle_factor = config.get("Algorithm", "distance_coefficient") # 主要修改这个变量
    # TODO: 这四个函数代码可以优化，由于我在循环中已经排除掉了所有自身比对的情况，因此此处不存在分母为0的情况。
    def dist(self, c1, c2):
        """
        calculate the distance between two points
        :param c1: the first point
        :param c2: the second point
        """
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5

    def T2S(self, T):
        """
        calculate the slope of the line
        :param T: the slope of the line
        """
        S = abs(T/((1+T**2)**0.5))
        return S

    def T2C(self, T):
        C = abs(1/((1+T**2)**0.5))
        return C

    def isclose(self, p1,p2):
        c_d = self.dist(p1[2], p2[2])
        if(p1[1] < p2[1]):
            a_w = p1[0]
            a_h = p1[1]
        else:
            a_w = p2[0]
            a_h = p2[1]
        T = 0
        try:
            T=(p2[2][1]-p1[2][1])/(p2[2][0]-p1[2][0])
        except ZeroDivisionError:
            T = 1.633123935319537e+16
        S = self.T2S(T)
        C = self.T2C(T)
        d_hor = C*c_d
        d_ver = S*c_d
        vc_calib_hor = a_w*1.3
        vc_calib_ver = a_h*0.4*self.angle_factor
        c_calib_hor = a_w *1.7
        c_calib_ver = a_h*0.2*self.angle_factor
        # print(p1[2], p2[2],(vc_calib_hor,d_hor),(vc_calib_ver,d_ver))
        if (0<d_hor<vc_calib_hor and 0<d_ver<vc_calib_ver):
            return 1
        elif (0<d_hor<c_calib_hor and 0<d_ver<c_calib_ver):
            return 2
        else:
            return 0