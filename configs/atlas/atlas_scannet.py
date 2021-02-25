model = dict(
    type='AtlasDetector',
    pretrained='open-mmlab://detectron/resnet50_caffe',
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=False),
        norm_eval=True,
        style='caffe'
    ),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=32,
        num_outs=4),
    neck_3d=dict(
        type='AtlasNeck',
        channels=[32, 64, 128, 256],
        out_channels=32,
        down_layers=[1, 2, 3, 4],
        up_layers=[3, 2, 1],
        conditional=False
    ),
    bbox_head=dict(
        type='VoxelFCOS3DHead',
        n_classes=18,
        in_channels=32
    )
)
train_cfg = dict(n_voxels=(160, 160, 64), voxel_size=.04)
# todo: increase n_voxels for test and val
test_cfg = dict(
    n_voxels=(160, 160, 64),
    voxel_size=.04,
    nms_pre=1000,
    iou_thr=.15,
    score_thr=.1)
img_norm_cfg = dict(mean=[102.9801, 115.9465, 122.7717], std=[1.0, 1.0, 1.0], to_rgb=False)

dataset_type = 'ScanNetMultiViewDataset'
data_root = 'data/scannet/'
class_names = ('cabinet', 'bed', 'chair', 'sofa', 'table', 'door', 'window',
               'bookshelf', 'picture', 'counter', 'desk', 'curtain',
               'refrigerator', 'showercurtrain', 'toilet', 'sink', 'bathtub',
               'garbagebin')

train_pipeline = [
    dict(type='LoadAnnotations3D'),
    dict(
        type='ScanNetMultiViewPipeline',
        n_images=7,
        transforms=[
            dict(type='LoadImageFromFile'),
            # dict(type='Pad', size=(972, 1296)),  # todo: ?
            dict(type='Resize', img_scale=(640, 480), keep_ratio=True),
            dict(type='Normalize', **img_norm_cfg)
        ]),
    dict(type='DefaultFormatBundle3D', class_names=class_names),
    dict(type='Collect3D', keys=['img', 'gt_bboxes_3d', 'gt_labels_3d'])
]
test_pipeline = [
    dict(
        type='ScanNetMultiViewPipeline',
        n_images=50,
        transforms=[
            dict(type='LoadImageFromFile'),
            # dict(type='Pad', size=(972, 1296)),  # todo: ?
            dict(type='Resize', img_scale=(640, 480), keep_ratio=True),
            dict(type='Normalize', **img_norm_cfg)
        ]),
    dict(type='DefaultFormatBundle3D', class_names=class_names, with_label=False),
    dict(type='Collect3D', keys=['img'])
]
data = dict(
    samples_per_gpu=1,
    workers_per_gpu=1,
    train=dict(
        type='RepeatDataset',
        times=1,
        dataset=dict(
            type=dataset_type,
            data_root=data_root,
            ann_file=data_root + 'scannet_infos_train.pkl',
            pipeline=train_pipeline,
            classes=class_names,
            filter_empty_gt=True,
            box_type_3d='Depth')),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'scannet_infos_val.pkl',
        pipeline=test_pipeline,
        classes=class_names,
        test_mode=True,
        box_type_3d='Depth'),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + 'scannet_infos_val.pkl',
        pipeline=test_pipeline,
        classes=class_names,
        test_mode=True,
        box_type_3d='Depth')
)

optimizer = dict(
    type='AdamW',
    lr=0.0001,
    weight_decay=0.0001,
    paramwise_cfg=dict(
        custom_keys={'backbone': dict(lr_mult=0.1, decay_mult=1.0)}))
optimizer_config = dict(grad_clip=dict(max_norm=35., norm_type=2))
lr_config = dict(policy='step', step=[8, 11])
total_epochs = 12

checkpoint_config = dict(interval=1, max_keep_ckpts=1)
log_config = dict(
    interval=1,  # todo: 50
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
evaluation = dict(interval=1)
dist_params = dict(backend='nccl')
find_unused_parameters = True  # todo: fix number of FPN outputs
log_level = 'INFO'
load_from = None
resume_from = None
workflow = [('train', 1)]

