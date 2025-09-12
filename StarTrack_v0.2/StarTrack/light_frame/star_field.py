
# dependencies
import math

import numpy as np
from PIL import Image, ImageFilter
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.utils import resample
from scipy.optimize import minimize
from scipy.ndimage import label

class Starfield:
    def __init__(self, state):
        self.state = state
        self.inputs = self.state.inputs

    def count_stars(self, *args):

        # create a list of possible cluster sizes, and empty output list
        if self.inputs.verbosity > 0:
            print("IN PROGRESS: Determining cluster number")

        # it can take incredibly long for this to run if the number of clusters is too high, so capped at 50
        if len(self.state.pixels_in_clusters) > 50:
            if self.inputs.verbosity > 0:
                print(f"IN PROGRESS: Trying up to 50 clusters!")
            cluster_size_list = range(2, 50)
        else:
            if self.inputs.verbosity > 0: print(f"Assessing up to {len(self.state.pixels_in_clusters)} clusters!")
            cluster_size_list = range(2, len(self.state.pixels_in_clusters))

        # loop through potential cluster sizes and produce silhouette scores
        silhouette_score_list = []

        # downsample the fitting data to speed up assessment if over 10,000 pixels identified
        max_n_pixels = 4000
        if len(self.state.pixels_in_clusters) > max_n_pixels:
            fitting_array = resample(self.state.pixels_in_clusters, n_samples=max_n_pixels, random_state=42)
        else:
            fitting_array = self.state.pixels_in_clusters

        # run an analysis with MiniBatchKMeans on fitting data to speed up assesment
        for k in cluster_size_list:
            kmeans = MiniBatchKMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(fitting_array)
            score = silhouette_score(fitting_array, labels)
            silhouette_score_list.append(score)

        # determine ideal number of clusters
        silhouette_score_list = np.array(silhouette_score_list)
        self.state.n_clusters = np.array(cluster_size_list)[np.argmax(silhouette_score_list)]

        # print outputs
        if self.inputs.verbosity > 0: print(f"{self.state.n_clusters} clusters detected in {self.inputs.frame_name}")

        # plot silhouette scores
        if self.inputs.verbosity > 1:
            plt.plot(cluster_size_list, silhouette_score_list, marker='o')
            plt.title("Silhouette Score vs Number of Clusters (KMeans)")
            plt.xlabel("Number of Clusters (k)")
            plt.ylabel("Silhouette Score")
            plt.grid(True)
            plt.show()

        return self

    def catalogue_properties(self, *args):

        # --- sub functions ---

        def local_density_filter(bounding_box, min_star_num):

            # in future releases this function, and the local_density_filter in the star_filter.py class, will be
            # refactored as a single method inside a new "utils2 class.

            # determine search radius
            star_detect_radius = 2

            # create empty array to store pixels identified as being in clusters
            arr_out = np.zeros(bounding_box.shape, dtype=np.uint8)

            # create star_pixels arrays
            star_pixels_yx = np.array(np.where(bounding_box == 255))
            star_pixels_y, star_pixels_x = star_pixels_yx

            # check every point, and log which pixels exceed the star detection radius
            for i_pixel in range(star_pixels_y.shape[0]):

                # define the bounds to be searched
                ref_y, ref_x = star_pixels_y[i_pixel], star_pixels_x[i_pixel]
                lower_x = ref_x - star_detect_radius
                upper_x = ref_x + star_detect_radius
                lower_y = ref_y - star_detect_radius
                upper_y = ref_y + star_detect_radius

                # check where mask overlaps and combine output into a single array
                mask_x = (star_pixels_x > lower_x) & (star_pixels_x < upper_x)
                mask_y = (star_pixels_y > lower_y) & (star_pixels_y < upper_y)
                mask_yx = mask_x & mask_y
                adjacent_star_pixels = np.vstack((star_pixels_y[mask_yx], star_pixels_x[mask_yx]))

                # we add 1 because filtered_stars will always have a minimum length of 1 (as the reference star will be in it)
                if adjacent_star_pixels.shape[1] > (min_star_num + 1):
                    # save the pixel co-ordinates to pixels in co-ordinates list
                    # self.state.pixels_in_clusters.append([ref_x, ref_y])

                    # add identified pixels to arr_out
                    arr_out[ref_y][ref_x] = 255

            return arr_out

        def count_stars_flood_fill(input_array):
            # a flood fill algorithm which will rapidly count stars, this is less accurate than the k-means clustering
            # used for more complex tasks, but it is good as a quick check here

            # flood fill sub-function which is called by all pixels that are searched
            def flood_fill(x_start, y_start):

                # initialise a co-ordinate search list, with tuples of individual co-ordinates inside
                search_coords = [(x_start, y_start)]

                # continue searching as long as there are pixels inside the search_coords list
                while search_coords:
                    # remove the x_start and y_start co-ordinates from the search_coords list, and extract them as x and y
                    x_search, y_search = search_coords.pop()

                    # make boundary check first
                    is_within_bounds = (0 <= x_search < height) and (0 <= y_search < width)

                    # if this check passes, check for bright pixels and if the pixel has previously been visited
                    if is_within_bounds:
                        is_bright_pixel = search_array[x_search, y_search] == 255
                        is_not_visited = not visited_array[x_search, y_search]

                        # if all conditions are satisfied, continue the search!
                        if is_bright_pixel and is_not_visited:
                            visited_array[x_search, y_search] = True

                            # four connected pixels are added
                            search_coords.extend([
                                (x_search - 1, y_search),
                                (x_search + 1, y_search),
                                (x_search, y_search - 1),
                                (x_search, y_search + 1)
                            ])

            # initialise
            search_array = input_array.copy()
            visited_array = np.zeros_like(search_array, dtype=bool)
            height, width = search_array.shape
            count = 0

            # search all bright pixels inside the search array
            for x_pixel in range(height):
                for y_pixel in range(width):

                    # if the bright pixel has not been identified as being connected to another bright pixel, run the algorithm and increase count by 1
                    if search_array[x_pixel, y_pixel] == 255 and not visited_array[x_pixel, y_pixel]:
                        flood_fill(x_pixel, y_pixel)
                        count += 1

            return count

        def calculate_cluster_centroid(i_cluster):

            def create_bounding_box(coords, perimeter_expansion):

                x_max = int(max(coords[:, 0]) + perimeter_expansion)
                x_min = int(min(coords[:, 0]) - perimeter_expansion)
                y_max = int(max(coords[:, 1]) + perimeter_expansion)
                y_min = int(min(coords[:, 1]) - perimeter_expansion)

                return x_max, x_min, y_max, y_min

            def fitness_function(x_guess):

                filtered_space = local_density_filter(star_in_bounding_box,x_guess)
                n = count_stars_flood_fill(filtered_space)
                residual = (n - 1)**2

                return residual

                # find the indices of all the labels
            i_label = np.where(labels == i_cluster)

            # find the coordinates of all stars in a cluster
            cluster_coords = self.state.pixels_in_clusters[i_label]

            # create the bounding box, finding the maximum and minimum x/y co-ordinates
            max_x, min_x, max_y, min_y = create_bounding_box(cluster_coords, perimeter_expansion=2)

            # create an array with just the cropped star in it - this uses .copy(), but really it should be refactored to not need copy
            star_in_bounding_box = self.state.mono_array[min_y:max_y, min_x:max_x].copy()

            # get thresholded box
            minor_stars_filter_threshold = self.inputs.threshold_value - 20
            threshold_bounding_box = np.where(star_in_bounding_box > minor_stars_filter_threshold, 255,0)

            threshold_bounding_img = Image.fromarray(threshold_bounding_box.astype(np.uint8))
            blur_bounding_img = threshold_bounding_img.filter(ImageFilter.GaussianBlur(radius=2))
            blur_array = np.array(blur_bounding_img)

            threshold_bounding_box = (blur_array > 100) * 255  # pixels above threshold become 255, others 0

            # plot bounding box
            if self.inputs.verbosity > 3:
                plt.imshow(threshold_bounding_box, cmap='gray')
                plt.show()

            # find n spots
            n_spots = count_stars_flood_fill(threshold_bounding_box)
            # print(n_spots)

            # find background intensity - currently not implemented!
            # background_coords = np.array(np.where(threshold_bounding_box == 0))
            # background_coords = background_coords.T
            # background_values = star_in_bounding_box[background_coords[:, 0], background_coords[:, 1]]
            # mean_background_intensity = np.mean(background_values)

            masked = np.zeros_like(self.state.mono_array)

            # check how many spots there are
            if n_spots == 1 or n_spots == 2:

                if n_spots == 1:
                    filtered_box = np.where(star_in_bounding_box < minor_stars_filter_threshold, 0, star_in_bounding_box)
                    masked[min_y:max_y, min_x:max_x] = filtered_box

                elif n_spots == 2:

                    # filter the data in the box to remove the smaller star and leave just the primary star
                    x0 = np.array([1])
                    result = minimize(fitness_function, x0, bounds=[(1,25)], method='L-BFGS-B')
                    filtered_box = local_density_filter(star_in_bounding_box, result.x)
                    masked[min_y:max_y, min_x:max_x] = filtered_box

                    # plot filtered box for debugging
                    if self.inputs.verbosity > 1:
                        plt.imshow(filtered_box, cmap='gray')
                        plt.show()

                # plot the filtered box mask overlaid on the frame for debugging
                if self.inputs.verbosity > 1:
                    plt.imshow(masked, cmap='gray')
                    plt.show()

                # find the intensity of the cluster
                cluster_intensity = int(np.sum(masked))

                # find the centroid by weighting against the intensity of each pixel
                y_indices, x_indices = np.indices(masked.shape)
                x_centroid = np.sum(x_indices * masked) / cluster_intensity
                y_centroid = np.sum(y_indices * masked) / cluster_intensity
                cluster_centroid = [float(x_centroid), float(y_centroid)]

                # on occasion, the code can isolate areas with an intensity of 0 but with a centroid location. the cause of this is currently unknown. this is a workaround.
                if cluster_intensity == 0:
                    cluster_intensity = np.nan
                    cluster_centroid = [np.nan, np.nan]

            # if over three stars are identified, assume it's a false detection and ignore
            else:
                cluster_intensity = np.nan
                cluster_centroid = [np.nan, np.nan]

            return cluster_centroid, cluster_intensity

        # --- main code ---

        # k means, labels for correct number of clusters
        kmeans = KMeans(n_clusters=self.state.n_clusters, random_state=42)
        labels = kmeans.fit_predict(self.state.pixels_in_clusters)

        # create empty output arrays for centroids and intensities
        centroid_list = np.empty((self.state.n_clusters, 2))
        intensity_list = np.empty(self.state.n_clusters)

        #  catalogue properties for each star - note that this will be unsorted!
        for i_star in range(0, self.state.n_clusters):
            centroid, intensity = calculate_cluster_centroid(i_star)
            centroid_list[i_star, :] = centroid
            intensity_list[i_star] = intensity

        # remove all NaNs, thereby returning lists which represent the true number of identified stars
        centroid_list = centroid_list[~np.isnan(centroid_list).any(axis=1)]
        intensity_list = intensity_list[~np.isnan(intensity_list)]

        # update the number of clusters to the number of actual positively identified stars
        self.state.n_clusters = len(intensity_list)
        self.state.centroid_list = centroid_list
        self.state.magnitude_list = np.array(np.bincount(labels)) # currently bincount is used as it is more robust than the intensity value calculated above

        # debugging information
        if self.inputs.verbosity > 1:
            print("Positions of stars:")
            print(self.state.centroid_list)
            print("Magnitude of stars:")
            print(self.state.magnitude_list)

        # plot identified stars
        if self.inputs.verbosity > 0:

            # create figure and load mono image
            plt.figure(figsize=(16, 12))
            plt.imshow(self.state.mono_array, cmap='gray')

            # plot a red circle around identified stars
            for i in range(self.state.n_clusters):
                x, y = self.state.centroid_list[i]
                marker_r = math.sqrt(self.state.magnitude_list[i]/math.pi)
                plt.scatter(x, y, facecolors='none', edgecolors='red', s=(marker_r+50))

            # plot identified stars 
            plt.title(f"{self.inputs.frame_name}: largest {self.state.n_clusters} stars detected inside search area")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.gca().invert_yaxis()
            plt.grid(False)
            plt.show()

        return self
