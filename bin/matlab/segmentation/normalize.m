function normed_feature = normalize(feature)

    normed_feature = (feature - min(feature(:))) / max(feature(:));
