
# dependencies
import math
import numpy as np
from PIL import Image, ImageFilter
from matplotlib import pyplot as plt
from StarTrack.light_frame.utils.main import Utils
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.utils import resample

class Starfield:
    def __init__(self, state):
        self.state = state
        self.inputs = self.state.inputs

    def count_stars(self, *args):

        # create a list of possible cluster sizes, and empty output list
        if self.inputs.verbosity > 0:
            print("IN PROGRESS: Determining cluster number")

        # it can take incredibly long for this to run if the number of clusters is too high, so capped at 50
        if len(self.state.pixels_in_clusters) > 100:
            if self.inputs.verbosity > 0:
                print(f"IN PROGRESS: Trying up to 100 clusters!")
            cluster_size_list = range(2, 100)
        else:
            if self.inputs.verbosity > 0: print(f"Assessing up to {len(self.state.pixels_in_clusters)} clusters!")
            cluster_size_list = range(2, len(self.state.pixels_in_clusters))

        # loop through potential cluster sizes and produce silhouette scores
        silhouette_score_list = []

        # downsample the fitting data to speed up assessment if over 10,000 pixels identified
        max_n_pixels = 2000
        if len(self.state.pixels_in_clusters) > max_n_pixels:
            fitting_array = resample(self.state.pixels_in_clusters, n_samples=max_n_pixels, random_state=42)
        else:
            fitting_array = self.state.pixels_in_clusters

        # run an analysis with MiniBatchKMeans on fitting data to speed up assesment
        for k in cluster_size_list:

            # mini batch k means is used to reduce computational overhead for initial calculations
            kmeans = MiniBatchKMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(fitting_array)

            # set to not use more than one thread, as this objects may be called within parallelisation
            score = silhouette_score(fitting_array, labels, n_jobs=1)
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

    def catalogue_detected_stars(self, *args):

        def catalogue_single_star(i_cluster):

            def count_spots(search_array):
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
                                    (x_search, y_search + 1)])

                # initialise
                search_array = search_array.copy()
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

            def bound_star(coords, perimeter_expansion):

                x_max = int(max(coords[:, 0]) + perimeter_expansion)
                x_min = int(min(coords[:, 0]) - perimeter_expansion)
                y_max = int(max(coords[:, 1]) + perimeter_expansion)
                y_min = int(min(coords[:, 1]) - perimeter_expansion)

                return x_max, x_min, y_max, y_min

            def isolate_largest_spot(detection_rad_guess):

                # r_guess: the initial guess for star detection radius
                # math.pi*r_iteration**2: min_star_num is updated, with the assumption that ALL pixels equivalent to the area of the MUST be filled!

                # define the properties of the solver:
                r_iteration = detection_rad_guess
                iteration_multiplier = 1.05 # the fidelity of each iteration
                iterate = True

                # perform the first calculation
                filtered_space = Utils.local_density_filter(search_array=bounded_star_threshold,star_detect_radius=r_iteration,star_detect_pixels=(math.pi * r_iteration ** 2))
                n_spots_iteration = count_spots(filtered_space)

                # continue to calculate values until the residual drops to 0
                while iterate:

                    # two exit conditions:
                    # 1) if n_spots_iteration is reduced to 0, it means that both stars were likely very similar in size, implying a large number of small stars
                    #    was falsely identified as a single large stars
                    # 2) if n_spots is reduced to 1, it means that a single large star has been successfully identified!
                    if n_spots_iteration <= 1:
                        iterate = False

                    # increase the value of the star detection radius:
                    r_iteration = r_iteration * iteration_multiplier

                    # update values
                    filtered_space = Utils.local_density_filter(search_array=bounded_star_threshold,star_detect_radius=r_iteration,star_detect_pixels=(math.pi * r_iteration ** 2))
                    n_spots_iteration = count_spots(filtered_space)

                return filtered_space

            def assess_star_symmetry(search_array):

                symmetry_score = 1

                return symmetry_score

            # find the indices of all the labels
            i_label = np.where(labels == i_cluster)

            # find the coordinates of all stars in a cluster
            cluster_coords = self.state.pixels_in_clusters[i_label]

            # create the bounding box, finding the maximum and minimum x/y co-ordinates
            max_x, min_x, max_y, min_y = bound_star(coords=cluster_coords, perimeter_expansion=2)

            # create an array with just the cropped star in it - this uses .copy(), but really it should be refactored to not need copy
            bounded_star = self.state.mono_array[min_y:max_y, min_x:max_x].copy()

            # provide a lower bound for star detection
            threshold = self.inputs.threshold - 20

            # threshold the bounded star to isolate the star and remove the background space
            bounded_star_threshold = np.where(bounded_star > threshold, 255, 0)

            # convert the bounded star threshold from an array into an image format
            bounded_star_threshold_img = Image.fromarray(bounded_star_threshold.astype(np.uint8))

            # blur the imaage to remove noise
            bounded_star_threshold_img_blur = bounded_star_threshold_img.filter(ImageFilter.GaussianBlur(radius=2))

            # convert the blurred image back to an array
            bounded_star_threshold_blur_array = np.array(bounded_star_threshold_img_blur)

            # update bounded_star_threshold with the blurred image instead,to reduce the impact of noise. pixels above threshold become 255, others 0
            bounded_star_threshold = (bounded_star_threshold_blur_array > 100) * 255

            # find the number of spots
            n_spots = count_spots(search_array=bounded_star_threshold)

            # delete data which is no longer required to free up memory
            del bounded_star_threshold_img, bounded_star_threshold_img_blur, bounded_star_threshold_blur_array

            # create empty mask of star field
            starfield_mask = np.zeros_like(self.state.mono_array)

            # check how many spots there are
            if 0 < n_spots < 6:

                if n_spots == 1:
                    bounded_star_filtered = np.where(bounded_star < threshold, 0, bounded_star) # can i just replace this with bounded_star_threshold
                    starfield_mask[min_y:max_y, min_x:max_x] = bounded_star_filtered

                elif 1 < n_spots < 6:

                    # calculate the radius of an average sized star
                    n_bright_pixels = np.array(np.where(bounded_star_threshold == 255)).shape[1]
                    mean_bright_spot_area = n_bright_pixels / n_spots
                    mean_bright_spot_radius = math.sqrt(mean_bright_spot_area/math.pi)
                    bounded_star_filtered = isolate_largest_spot(detection_rad_guess=mean_bright_spot_radius)
                    starfield_mask[min_y:max_y, min_x:max_x] = bounded_star_filtered

                    # plot filtered box for debugging
                    if self.inputs.verbosity > 1:
                        plt.imshow(bounded_star_filtered, cmap='gray')
                        plt.show()

                # plot the filtered box mask overlaid on the frame for debugging
                if self.inputs.verbosity > 1:
                    plt.imshow(starfield_mask, cmap='gray')
                    plt.show()

                # find the intensity of the cluster
                cluster_intensity = int(np.sum(starfield_mask))

                if cluster_intensity == 0:
                    cluster_intensity = np.nan
                    cluster_centroid = [np.nan, np.nan]
                else:
                    # find the centroid by weighting against the intensity of each pixel.
                    # in the case that the centroid cannot be calculated (value error, zero division error) label as NaN
                    try:
                        y_indices, x_indices = np.indices(starfield_mask.shape)
                        x_centroid = np.sum(x_indices * starfield_mask) / cluster_intensity
                        y_centroid = np.sum(y_indices * starfield_mask) / cluster_intensity
                        cluster_centroid = [float(x_centroid), float(y_centroid)]
                    except (ValueError, ZeroDivisionError):
                        cluster_intensity = np.nan
                        cluster_centroid = [np.nan, np.nan]

            # if over three stars are identified, assume it's a false detection and ignore
            else:
                cluster_intensity = np.nan
                cluster_centroid = [np.nan, np.nan]

            return cluster_centroid, cluster_intensity

        # k means, labels for correct number of clusters
        kmeans = KMeans(n_clusters=self.state.n_clusters, random_state=42)
        labels = kmeans.fit_predict(self.state.pixels_in_clusters)

        # create empty output arrays for centroids and intensities
        centroid_list = np.empty((self.state.n_clusters, 2))
        intensity_list = np.empty(self.state.n_clusters)

        #  catalogue properties for each star - note that this will be unsorted!
        for i_star in range(0, self.state.n_clusters):
            centroid, intensity = catalogue_single_star(i_star)
            centroid_list[i_star, :] = centroid
            intensity_list[i_star] = intensity

        # remove all NaNs, thereby returning lists which represent the true number of identified stars
        centroid_list = centroid_list[~np.isnan(centroid_list).any(axis=1)]
        intensity_list = intensity_list[~np.isnan(intensity_list)]

        # update the number of clusters to the number of actual positively identified stars
        self.state.n_clusters = len(intensity_list)
        self.state.centroid_list = centroid_list
        self.state.magnitude_list = intensity_list # currently bincount is used as it is more robust than the intensity value calculated above

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
