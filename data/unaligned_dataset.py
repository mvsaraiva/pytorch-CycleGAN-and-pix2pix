import os.path
from data.base_dataset import BaseDataset, get_transform
from data.image_folder import make_dataset
from PIL import Image
import random
import numpy as np

import torchvision.transforms as transforms
import torch


class UnalignedDataset(BaseDataset):
    """
    This dataset class can load unaligned/unpaired datasets.

    It requires two directories to host training images from domain A '/path/to/data/trainA'
    and from domain B '/path/to/data/trainB' respectively.
    You can train the model with the dataset flag '--dataroot /path/to/data'.
    Similarly, you need to prepare two directories:
    '/path/to/data/testA' and '/path/to/data/testB' during test time.
    """

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.dir_A = os.path.join(opt.dataroot, opt.phase + 'A')  # create a path '/path/to/data/trainA'
        self.dir_B = os.path.join(opt.dataroot, opt.phase + 'B')  # create a path '/path/to/data/trainB'

        print("#### data path ####")
        print(self.dir_A)

        self.A_paths = sorted(make_dataset(self.dir_A, opt.max_dataset_size))   # load images from '/path/to/data/trainA'
        self.B_paths = sorted(make_dataset(self.dir_B, opt.max_dataset_size))    # load images from '/path/to/data/trainB'

        print("self.A_paths: ")
        print(self.A_paths)

        self.A_size = len(self.A_paths)  # get the size of dataset A
        self.B_size = len(self.B_paths)  # get the size of dataset B
        btoA = self.opt.direction == 'BtoA'
        input_nc = self.opt.output_nc if btoA else self.opt.input_nc       # get the number of channels of input image
        output_nc = self.opt.input_nc if btoA else self.opt.output_nc      # get the number of channels of output image
        self.transform_A = get_transform(self.opt, grayscale=(input_nc == 1))   # get specified transforms for A
        self.transform_B = get_transform(self.opt, grayscale=(output_nc == 1))  # get specified transforms for B



    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index (int)      -- a random integer for data indexing

        Returns a dictionary that contains A, B, A_paths and B_paths
            A (tensor)       -- an image in the input domain
            B (tensor)       -- its corresponding image in the target domain
            A_paths (str)    -- image paths
            B_paths (str)    -- image paths
        """
        A_path = self.A_paths[index % self.A_size]  # make sure index is within then range
        if self.opt.serial_batches:   # make sure index is within then range
            index_B = index % self.B_size
        else:   # randomize the index for domain B to avoid fixed pairs.
            index_B = random.randint(0, self.B_size - 1)
        B_path = self.B_paths[index_B]


        # A_img = Image.open(A_path).convert('RGB')
        # B_img = Image.open(B_path).convert('RGB')




        print("Loading np arrays")

        # Modified for np array loading rather than image conversion
        A_img = np.load(A_path)
        B_img = np.load(B_path)

        B_img = np.reshape(B_img, (43,43,50)) # Make sure to change this to be more general or smth

        # conversion to tensor first, conversion to double
        # toTensorTransformList = []
        # toTensorTransformList += [transforms.ToTensor()]
        # toTensorTransform = transforms.Compose(toTensorTransformList)
        # A_img = toTensorTransform(A_img)
        # B_img = toTensorTransform(B_img)

        A_img = torch.from_numpy(A_img)
        B_img = torch.from_numpy(B_img)

        # A_img = A_img.type(torch.DoubleTensor) 
        # B_img = B_img.type(torch.DoubleTensor) 

        print("SHAPES OF TENSOR::")
        print(A_img.shape)
        print(B_img.shape)



        # apply image transformation (but not really, since we're not using images), just leaving for code consistency
        print("Applying transforms")
        A = self.transform_A(A_img)
        B = self.transform_B(B_img)
        print("Transforms success!")

        return {'A': A, 'B': B, 'A_paths': A_path, 'B_paths': B_path}

    def __len__(self):
        """Return the total number of images in the dataset.

        As we have two datasets with potentially different number of images,
        we take a maximum of
        """
        return max(self.A_size, self.B_size)
