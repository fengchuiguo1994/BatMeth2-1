/*
 *  ssw.h
 *
 *  Created by Mengyao Zhao on 6/22/10.
 *  Copyright 2010 Boston College. All rights reserved.
 *	Version 0.1.4
 *	Last revision by Mengyao Zhao on 04/18/12.
 *
 */

#ifndef SSW_H
#define SSW_H

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <emmintrin.h>
#ifdef DYNAMIC_ZLIB
  #include <zlib.h>
#else
  #include "zlib.h"
#endif
#include "kseq.h"


KSEQ_INIT(gzFile, gzread)
/*!	@typedef	structure of the query profile	*/
struct _profile;
typedef struct _profile s_profile;

/*!	@typedef	structure of the alignment result
	@field	score1	the best alignment score
	@field	mismatch_count	number of mismatch
	@field	gap_count	number of gap
	
	@field	score2	sub-optimal alignment score
	@field	ref_begin1	best alignment beginning position on reference;	ref_begin1 = 0 when the best alignment beginning position 
						is not available
	@field	ref_end1	best alignment ending position on reference
	@field	read_begin1	best alignment beginning position on read; read_begin1 = 0 when the best alignment beginning position is 
						not available
	@field	read_end1	best alignment ending position on read
	@field	read_end2	sub-optimal alignment ending position on read
	@field	cigar	best alignment cigar; stored the same as that in BAM format, high 28 bits: length, low 4 bits: M/I/D (0/1/2); 
					cigar = 0 when the best alignment path is not available
	@field	cigarLen	length of the cigar string; cigarLen = 0 when the best alignment path is not available
	@note	The fields ref_begin1, ref_end1, read_begin1 read_end1 and read_end2 all have 1-based coordinates.
*/
typedef struct {
	uint16_t score1;
	uint16_t mismatch_count;
	uint16_t match_count;
	uint16_t gap_count;
	
	uint16_t score2;	
	int32_t ref_begin1;	
	int32_t ref_end1;	
	int32_t	read_begin1;	
	int32_t read_end1;	
	int32_t ref_end2;
	uint32_t* cigar;	
	int32_t cigarLen;	
} s_align;

#ifdef __cplusplus
extern "C" {
#endif	// __cplusplus

/*!	@function	Create the query profile using the query sequence.
	@param	read	pointer to the query sequence; the query sequence needs to be numbers
	@param	readLen	length of the query sequence
	@param	mat	pointer to the substitution matrix; mat needs to be corresponding to the read sequence
	@param	n	the square root of the number of elements in mat (mat has n*n elements)
	@param	score_size	estimated Smith-Waterman score; if your estimated best alignment score is surely < 255 please set 0; if 
						your estimated best alignment score >= 255, please set 1; if you don't know, please set 2 
	@return	pointer to the query profile structure
	@note	example for parameter read and mat:
			If the query sequence is: ACGTATC, the sequence that read points to can be: 1234142
			Then if the penalty for match is 2 and for mismatch is -2, the substitution matrix of parameter mat will be:
			//A  C  G  T  
			  2 -2 -2 -2 //A
			 -2  2 -2 -2 //C
			 -2 -2  2 -2 //G
			 -2 -2 -2  2 //T
			mat is the pointer to the array {2, -2, -2, -2, -2, 2, -2, -2, -2, -2, 2, -2, -2, -2, -2, 2}
*/
s_profile* ssw_init (const int8_t* read, const int32_t readLen, const int8_t* mat, const int32_t n, const int8_t score_size);

/*!	@function	Release the memory allocated by function ssw_init.
	@param	p	pointer to the query profile structure	
*/
void init_destroy (s_profile* p);

// @function	ssw alignment.
/*!	@function	Do Striped Smith-Waterman alignment.
	@param	prof	pointer to the query profile structure
	@param	ref	pointer to the target sequence; the target sequence needs to be numbers and corresponding to the mat parameter of
				function ssw_init
	@param	refLen	length of the target sequence
	@param	weight_gapO	the absolute value of gap open penalty  
	@param	weight_gapE	the absolute value of gap extension penalty
	@param	flag	bitwise FLAG; (from high to low) bit 5: when setted as 1, function ssw_align will return the best alignment 
					beginning position; bit 6: when setted as 1, if (ref_end1 - ref_begin1 < filterd && read_end1 - read_begin1 
					< filterd), (whatever bit 5 is setted) the function will return the best alignment beginning position and 
					cigar; bit 7: when setted as 1, if the best alignment score >= filters, (whatever bit 5 is setted) the function
  					will return the best alignment beginning position and cigar; bit 8: when setted as 1, (whatever bit 5, 6 or 7 is
 					setted) the function will always return the best alignment beginning position and cigar
	@param	filters	when bit 7 of flag is setted as 1 and bit 8 is setted as 0, filters will be used
	@param	filterd	when bit 6 of flag is setted as 1 and bit 8 is setted as 0, filterd will be used
	@return	pointer to the alignment result structure 
	@note	Whatever the parameter flag is setted, this function will at least return the optimal and sub-optimal alignment score,
			and the optimal alignment ending positions on target and query sequences. If both bit 6 and 7 of the flag are setted
			while bit 8 is not, the function will return cigar only when both criteria are fulfilled. All returned positions are 
			0-based coordinate.  	
*/
s_align* ssw_align (const s_profile* prof, 
					const int8_t* ref, 
					int32_t refLen, 
					const uint8_t weight_gapO, 
					const uint8_t weight_gapE, 
					const uint8_t flag,	
					const uint16_t filters,
					const int Skip_DP,
					const int32_t filterd);

/*!	@function	Release the memory allocated by function ssw_align.
	@param	a	pointer to the alignment result structure
*/
void align_destroy (s_align* a);

void init_SSW_BS_g2a();
void init_SSW_BS_c2t();
void init_SSW(); 
void init_SSW_Clip(int32_t match,int32_t  mismatch,int32_t  gap_open,int32_t  gap_extension);
s_align* ssw_write (s_align* a, 
			kseq_t* ref_seq,
			kseq_t* read);
s_align* mengyao_ssw_core (
		char *pacseq,//Refernce seq(this is the pacseq),len
		int len,//orignal seq length.. 
		char *seq,//Original seq... 
		int reflen,//length of reference string..
		int filter,
		int Skip_DP,
		s_profile* p
		);
#ifdef __cplusplus
}
#endif	// __cplusplus

#endif	// SSW_H
