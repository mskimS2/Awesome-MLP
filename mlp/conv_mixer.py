import torch
import torchsummary
from torch import nn


class ConvMixer(nn.Module):

    def __init__(
        self,
        in_channels: int,
        hidden_dim: int,
        n_layers: int,
        kernel_size: int = 5,
        patch_size: int = 2,
        num_classes: int = 10
    ) -> None:
        super(ConvMixer, self).__init__()

        sublayer = nn.Sequential(
            nn.Conv2d(
                hidden_dim,
                hidden_dim,
                kernel_size,
                groups=hidden_dim,
                padding='same'
            ),
            nn.GELU(),
            nn.BatchNorm2d(hidden_dim)
        )
        self.convmixer_layers = nn.Sequential(
            nn.Conv2d(
                in_channels,
                hidden_dim,
                kernel_size=patch_size,
                stride=patch_size
            ),
            nn.GELU(),
            nn.BatchNorm2d(hidden_dim),
            *[
                nn.Sequential(
                    ResidualLayer(sublayer),
                    nn.Conv2d(hidden_dim, hidden_dim, kernel_size=1),
                    nn.GELU(),
                    nn.BatchNorm2d(hidden_dim)
                ) for _ in range(n_layers)
            ],
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.convmixer_layers(x)
        return self.classifier(x)


class ResidualLayer(nn.Module):
    def __init__(self, layer: nn.Module) -> None:
        super(ResidualLayer, self).__init__()
        self.layer = layer

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layer(x) + x


if __name__ == '__main__':
    import torchsummary

    # test code
    convmixer = ConvMixer(
        in_channels=3,
        hidden_dim=256,
        n_layers=8,
        kernel_size=12,
        patch_size=4,
        num_classes=10
    )

    torchsummary.summary(convmixer.cuda(), (3, 32, 32))
