plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
    // Google services plugin for Firebase
    id("com.google.gms.google-services")
}

android {
    namespace = "com.example.gym_frontend"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.example.gym_frontend"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    flavorDimensions += "app"
    productFlavors {
        create("client") {
            dimension = "app"
            applicationIdSuffix = ".client"
            versionNameSuffix = "-client"
            resValue("string", "app_name", "Gym Client")
        }
        create("staff") {
            dimension = "app"
            applicationIdSuffix = ".staff"
            versionNameSuffix = "-staff"
            resValue("string", "app_name", "Gym Staff")
        }
        create("superAdmin") {
            dimension = "app"
            applicationIdSuffix = ".superadmin"
            versionNameSuffix = "-superadmin"
            resValue("string", "app_name", "Platform Admin")
        }
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

dependencies {
    // Firebase BoM — keeps all Firebase library versions in sync
    implementation(platform("com.google.firebase:firebase-bom:34.9.0"))
    // Firebase Cloud Messaging
    implementation("com.google.firebase:firebase-messaging")
}

flutter {
    source = "../.."
}
