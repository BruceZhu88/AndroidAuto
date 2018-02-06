
import cv2
import aircv as ac


def draw_circle(img, pos, circle_radius, color, line_width):
    cv2.circle(img, pos, circle_radius, color, line_width)
    cv2.imshow('objDetect', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def coordinate(src, obj):
    im_src = ac.imread(src)
    im_obj = ac.imread(obj)
    pos = ac.find_template(im_src, im_obj)
    return int(pos['result'][0]), int(pos['result'][1])


if __name__ == "__main__":
    path = r'D:/bruce/workspace/workspace/Opencv/src/'
    src_pic = path + 'test.png'
    obj_pic = path + 'allow.png'
    pos = coordinate(src_pic, obj_pic)
    circle_center_pos = pos
    circle_radius = 50
    color = (0, 255, 0)
    line_width = 10

    print(circle_center_pos)
    # draw circle
    im_src = ac.imread(src_pic)
    draw_circle(im_src, circle_center_pos, circle_radius, color, line_width)
