import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/providers/gym_branding_provider.dart';
import '../../../shared/models/gym_model.dart';
import '../../../shared/widgets/loading_indicator.dart';

/// Three-step wizard shown when a gym owner logs in for the first time.
///
/// Step 1 — Gym Name
/// Step 2 — Logo Upload
/// Step 3 — Brand Colors (primary + secondary)
///
/// On completion the branding provider is updated and the owner is sent
/// to their normal dashboard.
class GymSetupWizard extends StatefulWidget {
  const GymSetupWizard({super.key});

  @override
  State<GymSetupWizard> createState() => _GymSetupWizardState();
}

class _GymSetupWizardState extends State<GymSetupWizard> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  bool _isSubmitting = false;

  // Step 1 — Gym Name
  final _gymNameController = TextEditingController();
  final _gymNameFormKey = GlobalKey<FormState>();

  // Step 2 — Logo
  String? _selectedLogoUrl;
  // In a real implementation you'd use image_picker to pick a file and upload.
  // For now we accept a URL or show a placeholder illustrating the flow.

  // Step 3 — Colors
  Color _selectedPrimary = const Color(0xFFDC2626);
  Color _selectedSecondary = const Color(0xFFEF4444);

  // Pre-defined palette the owner can pick from
  static const List<Color> _colorPalette = [
    Color(0xFFDC2626), // Red
    Color(0xFFEF4444), // Light Red
    Color(0xFFB91C1C), // Dark Red
    Color(0xFFF97316), // Orange
    Color(0xFFF59E0B), // Amber
    Color(0xFF10B981), // Emerald
    Color(0xFF14B8A6), // Teal
    Color(0xFF3B82F6), // Blue
    Color(0xFF6366F1), // Indigo
    Color(0xFF8B5CF6), // Violet
    Color(0xFFA855F7), // Purple
    Color(0xFFEC4899), // Pink
    Color(0xFF06B6D4), // Cyan
    Color(0xFF84CC16), // Lime
    Color(0xFF78716C), // Stone
    Color(0xFF64748B), // Slate
  ];

  @override
  void dispose() {
    _pageController.dispose();
    _gymNameController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep == 0) {
      if (!_gymNameFormKey.currentState!.validate()) return;
    }
    if (_currentStep < 2) {
      setState(() => _currentStep++);
      _pageController.animateToPage(
        _currentStep,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      _submitSetup();
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
      _pageController.animateToPage(
        _currentStep,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _submitSetup() async {
    setState(() => _isSubmitting = true);

    try {
      final branding = context.read<GymBrandingProvider>();
      final apiService = context.read<ApiService>();

      // Build hex strings from selected colors
      final primaryHex = '#${_selectedPrimary.value.toRadixString(16).substring(2).toUpperCase()}';
      final secondaryHex = '#${_selectedSecondary.value.toRadixString(16).substring(2).toUpperCase()}';

      // Send to backend
      final response = await apiService.put('/api/gyms/setup', data: {
        'name': _gymNameController.text.trim(),
        'primary_color': primaryHex,
        'secondary_color': secondaryHex,
        if (_selectedLogoUrl != null) 'logo_url': _selectedLogoUrl,
        'is_setup_complete': true,
      });

      final responseData = response.data;
      final gymJson = responseData['data'] as Map<String, dynamic>?;

      // Update local provider
      if (gymJson != null) {
        branding.loadFromGym(GymModel.fromJson(gymJson));
      } else {
        branding.updateBranding(
          gymName: _gymNameController.text.trim(),
          primaryColor: _selectedPrimary,
          secondaryColor: _selectedSecondary,
          logoUrl: _selectedLogoUrl,
          isSetupComplete: true,
        );
      }

      if (mounted) {
        // Navigate to owner dashboard — GoRouter redirect handles it
        context.go('/owner');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final labels = ['Gym Name', 'Logo', 'Brand Colors'];

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Header with progress
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 24, 24, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Set Up Your Gym',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Step ${_currentStep + 1} of 3 — ${labels[_currentStep]}',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[500],
                        ),
                  ),
                  const SizedBox(height: 16),

                  // Progress bar
                  Row(
                    children: List.generate(3, (i) {
                      final isActive = i <= _currentStep;
                      return Expanded(
                        child: Container(
                          height: 4,
                          margin: EdgeInsets.only(right: i < 2 ? 8 : 0),
                          decoration: BoxDecoration(
                            color: isActive
                                ? Theme.of(context).colorScheme.primary
                                : Colors.grey[700],
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      );
                    }),
                  ),
                ],
              ),
            ),

            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  _buildStep1GymName(context),
                  _buildStep2Logo(context),
                  _buildStep3Colors(context),
                ],
              ),
            ),

            // Navigation buttons
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                children: [
                  if (_currentStep > 0)
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _isSubmitting ? null : _previousStep,
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: const Text('Back'),
                      ),
                    ),
                  if (_currentStep > 0) const SizedBox(width: 16),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: _isSubmitting ? null : _nextStep,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: _isSubmitting
                          ? const SmallLoadingIndicator()
                          : Text(
                              _currentStep < 2 ? 'Continue' : 'Finish Setup',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // STEP 1 — Gym Name
  // ─────────────────────────────────────────────────────────────
  Widget _buildStep1GymName(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Form(
        key: _gymNameFormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 40),

            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.fitness_center,
                size: 64,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(height: 32),

            Text(
              'What\'s your gym called?',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'This will appear as the app name for all your staff and customers.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[500],
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),

            TextFormField(
              controller: _gymNameController,
              decoration: const InputDecoration(
                labelText: 'Gym Name',
                hintText: 'e.g. Body Art Fitness',
                prefixIcon: Icon(Icons.store),
              ),
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 18),
              textCapitalization: TextCapitalization.words,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter your gym name';
                }
                if (value.trim().length < 2) {
                  return 'Name must be at least 2 characters';
                }
                return null;
              },
            ),

            const SizedBox(height: 24),

            // Preview
            if (_gymNameController.text.trim().isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[700]!),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.email, size: 16, color: Colors.grey),
                    const SizedBox(width: 8),
                    Text(
                      'Customer emails: name@${_gymNameController.text.trim().toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '')}.com',
                      style: TextStyle(color: Colors.grey[400], fontSize: 13),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // STEP 2 — Logo
  // ─────────────────────────────────────────────────────────────
  Widget _buildStep2Logo(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 40),

          Text(
            'Upload Your Gym Logo',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'This will be shown on the login screen and app header.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[500],
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),

          // Logo upload area
          GestureDetector(
            onTap: () {
              // TODO: Implement image_picker when the dependency is added
              // For now, show a placeholder dialog
              _showLogoUrlDialog();
            },
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
                  width: 2,
                  strokeAlign: BorderSide.strokeAlignOutside,
                ),
              ),
              child: _selectedLogoUrl != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: Image.network(
                        _selectedLogoUrl!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => _buildUploadPlaceholder(context),
                      ),
                    )
                  : _buildUploadPlaceholder(context),
            ),
          ),

          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: () => _showLogoUrlDialog(),
            icon: Icon(
              _selectedLogoUrl != null ? Icons.edit : Icons.cloud_upload,
              size: 18,
            ),
            label: Text(_selectedLogoUrl != null ? 'Change Logo' : 'Upload Logo'),
          ),

          const SizedBox(height: 24),

          // Skip hint
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, size: 16, color: Colors.grey[500]),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'You can skip this for now and add a logo later from Settings.',
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUploadPlaceholder(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.add_photo_alternate_outlined,
          size: 48,
          color: Theme.of(context).colorScheme.primary.withOpacity(0.6),
        ),
        const SizedBox(height: 8),
        Text(
          'Tap to upload',
          style: TextStyle(
            color: Colors.grey[500],
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  void _showLogoUrlDialog() {
    final controller = TextEditingController(text: _selectedLogoUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logo URL'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'https://example.com/logo.png',
            labelText: 'Image URL',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() => _selectedLogoUrl = controller.text.trim().isEmpty ? null : controller.text.trim());
              Navigator.pop(ctx);
            },
            child: const Text('Set Logo'),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // STEP 3 — Brand Colors
  // ─────────────────────────────────────────────────────────────
  Widget _buildStep3Colors(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 32),

          Text(
            'Choose Your Brand Colors',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'These colors will be used throughout the app for your gym.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[500],
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),

          // Primary color picker
          Text(
            'Primary Color',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Used for buttons, highlights, and accents',
            style: TextStyle(color: Colors.grey[500], fontSize: 13),
          ),
          const SizedBox(height: 16),
          _buildColorGrid(
            selectedColor: _selectedPrimary,
            onColorSelected: (c) => setState(() => _selectedPrimary = c),
          ),

          const SizedBox(height: 32),

          // Secondary color picker
          Text(
            'Secondary Color',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Used for secondary elements and accents',
            style: TextStyle(color: Colors.grey[500], fontSize: 13),
          ),
          const SizedBox(height: 16),
          _buildColorGrid(
            selectedColor: _selectedSecondary,
            onColorSelected: (c) => setState(() => _selectedSecondary = c),
          ),

          const SizedBox(height: 32),

          // Preview
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  _selectedPrimary.withOpacity(0.15),
                  _selectedSecondary.withOpacity(0.08),
                ],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _selectedPrimary.withOpacity(0.4)),
            ),
            child: Column(
              children: [
                Text(
                  'Preview',
                  style: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  _gymNameController.text.trim().isEmpty
                      ? 'Your Gym'
                      : _gymNameController.text.trim(),
                  style: TextStyle(
                    color: _selectedPrimary,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _selectedPrimary,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Primary'),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: () {},
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _selectedSecondary,
                        side: BorderSide(color: _selectedSecondary),
                      ),
                      child: const Text('Secondary'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildColorGrid({
    required Color selectedColor,
    required ValueChanged<Color> onColorSelected,
  }) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: _colorPalette.map((color) {
        final isSelected = color.value == selectedColor.value;
        return GestureDetector(
          onTap: () => onColorSelected(color),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected ? Colors.white : Colors.transparent,
                width: 3,
              ),
              boxShadow: isSelected
                  ? [
                      BoxShadow(
                        color: color.withOpacity(0.6),
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ]
                  : null,
            ),
            child: isSelected
                ? const Icon(Icons.check, color: Colors.white, size: 20)
                : null,
          ),
        );
      }).toList(),
    );
  }
}
