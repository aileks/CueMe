import os

from playlist_generator import PlaylistGenerator


def train_playlist_model():
    """Train the playlist recommendation model using existing CSV files"""
    csv_files = [
        os.path.join(os.path.dirname(__file__), "../data", "spotify-dataset.csv"),
        os.path.join(os.path.dirname(__file__), "../data", "combined-dataset.csv"),
    ]

    generator = PlaylistGenerator(model_path="app/ml/pretrained/playlist_model.joblib")

    print("Loading data...")
    success = generator.load_data(csv_files)
    if not success:
        print("Failed to load data")
        return

    print("Training model...")
    success = generator.train(save_model=True)

    if success:
        print("Model trained successfully!")

        if generator.tracks_df is not None:
            print(f"Total tracks in dataset: {len(generator.tracks_df)}")

            print("\nSample tracks:")
            for _, track in generator.tracks_df.sample(5).iterrows():
                print(
                    f"{track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')} | "
                    f"Danceability: {track.get('danceability', 'N/A')}, "
                    f"Loudness: {track.get('loudness', 'N/A')}"
                )
        else:
            print("No tracks data available")
    else:
        print("Training failed.")


if __name__ == "__main__":
    train_playlist_model()
