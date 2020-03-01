import cv2

from ServiceRunner.ConfigReader import NNConfig
from ServiceRunner.NeuralEngine import NetHandler, process_output
from ServiceRunner.Tools import read_items, draw_item, PathManager


class Player:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.index = 0
        self.wait_time = 0

    def disp(self, set_id=None, net_handler=None):
        path_manager = PathManager(root_dir)
        if set_id is None:
            path_manager.use_last()
        else:
            path_manager.use_set_id(set_id)
        items = read_items(path_manager.log_path)
        images_paths = path_manager.list_images()
        while True:
            image_path = images_paths[self.index]
            item = items[self.index]
            image = cv2.imread(image_path)
            if net_handler is not None:
                net_handler.load(image)
                out = net_handler.infer()
                frame_items = process_output(out, 0, 0, 17)
                for frame_item in frame_items:
                    draw_item(image, frame_item, (0, 0, 255))
            draw_item(image, item)
            cv2.putText(image, f"N: {self.index}", (5, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("image", image)
            k = cv2.waitKeyEx(self.wait_time)
            if k == 2555904:  # Right
                self.index += 1
            elif k == 2424832:  # Left
                self.index -= 1
            elif k == 2490368:  # Up
                pass
            elif k == 2621440:  # Down
                pass
            elif k == 27:  # Down
                cv2.destroyAllWindows()
                break
            elif k == ord('t'):  # timed view
                if self.wait_time == 0:
                    self.wait_time = int((items[-1].time - items[0].time) * 1000 // len(items))
                else:
                    self.wait_time = 0
            elif k == -1:
                self.index += 1
            else:
                print(f"k = {k} not assigned")

            self.index = min(max(self.index, 0), len(items) - 1)

    def vid(self, sed_id=None):
        path_manager = PathManager(root_dir)
        if set_id is None:
            path_manager.use_last()
        else:
            path_manager.use_set_id(set_id)
        items = read_items(path_manager.log_path)
        images_paths = path_manager.list_images()
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        # fourcc = cv2.VideoWriter_fourcc(*"MP4V    ")
        frame_rate = len(items) / (items[-1].time - items[0].time)
        print(f"Framerate : {frame_rate}")
        image_path = images_paths[0]
        image = cv2.imread(image_path)
        out = cv2.VideoWriter(f'video_{set_id}.mp4', fourcc, frame_rate, (image.shape[1], image.shape[0]))
        for image_path, item in zip(images_paths, items):
            image = cv2.imread(image_path)
            image = cv2.flip(image, 1)
            item.xmin = 1 - item.xmin
            item.xmax = 1 - item.xmax
            draw_item(image,item)
            out.write(image)
            cv2.imshow("image", image)
            cv2.waitKey(1)
        out.release()
        cv2.destroyAllWindows()


set_id = 15
root_dir = ".\Images"

player = Player(root_dir)
nn_config = NNConfig()
nn_config.target_label = 17
nn_config.image_height = 300
nn_config.image_width = 300
nn_config.model_xml_path = "Models/ssd_mobilenet_v2_coco/FP32/ssd_mobilenet_v2_coco.xml"
# net_handler = NetHandler(nn_config)
# player.disp(set_id)
player.vid(set_id)
