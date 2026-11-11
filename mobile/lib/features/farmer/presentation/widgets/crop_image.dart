import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';

class CropImage extends StatelessWidget {
  const CropImage({
    super.key,
    required this.url,
    this.height,
    this.width,
    this.fit = BoxFit.cover,
    this.iconSize = 28,
  });

  final String url;
  final double? height;
  final double? width;
  final BoxFit fit;
  final double iconSize;

  bool get _hasValidUrl {
    final uri = Uri.tryParse(url.trim());
    return uri != null &&
        (uri.scheme == 'http' || uri.scheme == 'https') &&
        uri.host.isNotEmpty;
  }

  @override
  Widget build(BuildContext context) {
    if (!_hasValidUrl) return _placeholder();
    return Image.network(
      url.trim(),
      height: height,
      width: width,
      fit: fit,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return ColoredBox(
          color: AppTheme.primaryTint,
          child: SizedBox(
            height: height,
            width: width,
            child: Center(
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: AppTheme.primary,
                value: loadingProgress.expectedTotalBytes != null
                    ? loadingProgress.cumulativeBytesLoaded /
                        loadingProgress.expectedTotalBytes!
                    : null,
              ),
            ),
          ),
        );
      },
      errorBuilder: (_, _, _) => _placeholder(),
    );
  }

  Widget _placeholder() {
    return ColoredBox(
      color: AppTheme.primaryTint,
      child: SizedBox(
        height: height,
        width: width,
        child: Icon(
          Icons.image_not_supported_outlined,
          size: iconSize,
          color: AppTheme.primary,
        ),
      ),
    );
  }
}
